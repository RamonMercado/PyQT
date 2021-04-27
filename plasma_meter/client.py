import asyncio
import logging
import datetime
from asyncua import Client
import csv


class DataClient:
    """
    OPC-UA Asynchronous Data Client

    NOTE: attributes that are specified in the format
          'Node, data_type' mean that the attribute is an OPC-UA
          node that holds the specified data type

    Attributes:
    __________
    __server_url: str
        IP and Port to grab OPC-UA data from.
        Format:  opc.tcp://[IP]:[PORT]
    __address_space_name: str
        address space from OPC-UA server to get data from
    __client: Client
        asynchronous OPC-UA client
    __is_client_done: bool
        if ture, client is done retrieving measurements

    current_list: list
        holds calculated currents from the plasma sensor
    time_list: list
        holds the times at which the currents were calculated from the plasma sensor
    voltage_list: list
        list of voltages (these voltages act as the voltage ramp) passed onto the plasma sensor

    __address_space: Node
        OPC-UA server address space

    __selected_voltage_ramp: list
        list of voltages to apply to plasma sensor
        Holds the value entered onto the client when object is instantiated
    __selected_voltage_sweep_time: float
        wait time between measurements (in .1 seconds)
        Holds the value entered onto the client when object is instantiated
    __selected_current_filter: str
        data filter to apply to final list of current
        Holds the value entered onto the client when object is instantiated
                               Values: 'None' -> No filter applied
                                       'SOS' -> SOS filter
    __selected_sensor_to_use: str
        Plasma sensor to use for measurements
        Holds the value entered onto the client when object is instantiated
                                Values: 'SLP', 'DLP', 'HEA'
                                SLP -> Single Langmuir Probe
                                DLP -> Double Langmuir Probe
                                HEA -> Hyperbolic Energy Analyzer
    __selected_gas: str
        Gas used during plasma measurements
        Holds the value entered onto the client when object is instantiated
    __selected_magnetic_field: str
        Magnetic field to be used during measurements

    __voltage_ramp: Node, list
        list of voltages to apply to plasma sensor
    __voltage_sweep_time: Node, float
         wait time between measurements (in .1 seconds)
    __current_filter: Node, str
         data filter to apply to final list of current
    __sensor_to_use: Node, str
         Plasma sensor to use for measurements

    __abort_measurements: Node, bool
        Signals the server to abort a measurement
    __is_client_data_fully_sent: Node, bool
        Client signal that it has finished sending measurement parameter
    __is_measurements_running: Node, bool
         Specifies if the server is running a measurement
    __is_measurements_finished: Node, bool
         Server signal that specifies that it has finished calculating measurements

     __current_measurements: Node, str
        Holds the calculated 'current' from the plasma sensor
    __time_measurements: Node, str
        Times in which the plasma sensor's current was calculated

    Methods:
    -------
    __initialize_client():
        Initializes the client and all nodes that are handled by the server and used by the client
    __send_measurement_parameters_to_server(self):
        Sends the measurement parameters to the server
    __fix_current_and_time_data_types(self):
        Fixes the data types of the current and time measurements nodes sent by the server.
        Changes them from strings to lists.

    start_client():
        Sends measurement data to server and awaits measurement data.
        Gets the server data asynchronously on server url.
    set_measurement_parameters(voltage_ramp: list, voltage_sweep_time: float, sensor_to_use: str,
                                   gas: str = 'Air', current_filter: str = 'None'):
        Sets the parameters to use for plasma measurements
    stop_listening():
        Stop listening for server data

    set_server_url(server_url: str):
        Change server url server will serve data on
    get_server_url():
        Returns server url server will serve data on
    get_sensor_used():
        Gets the type of sensor used for plasma measurements
    get_gas():
        Gets the gas used for plasma measurements
     get_magnetic_field():
        Returns the magnetic field used during measurements
    get_voltage_list():
        Returns list of voltages (these voltages act as the voltage ramp) passed onto the plasma sensor
    get_current_list():
        Returns calculated currents from the plasma sensor
    get_time_list():
        Returns times at which the currents were calculated from the plasma sensor
    is_client_done():
        Returns true if the client has received all data for all measurements from the server


    The following data is shared by the server to all clients:
    ----------------------------------------------------------
    class Sensor:
        voltage_ramp: list, writeable
            List specifying all voltages to read from a plasma sensor.
            Format: [2, 2.5, 3] -> all values are voltages

        voltage_sweep_time: int, writeable
            Wait time between measurements (in seconds)

        current_filter: str, writeable
            Data filter to apply to final list of current
            Values: 'None' -> No filter applied
                    'SOS' -> SOS filter

        sensor_to_use: str, writeable
            Plasma sensor to use for measurement
            Values: 'SLP', 'DLP', 'HEA'
            SLP -> Single Langmuir Probe
            DLP -> Double Langmuir Probe
            HEA -> Hyperbolic Energy Analyzer

        abort_measurements: bool, writeable
            if set to true, aborts running measurements

        is_client_data_fully_sent: bool, writeable
            if set to true, client data has been fully received and measurement can be run

        is_measurements_running: bool, not writeable
            if set to true, server is currently running measurements

        is_measurements_finished: bool, not writeable
            if set to true, server is done calculating measurements

        NOTE: the current measurements and time measurements holders are currently implemented as string
        data structures. this should be changed to use lists as it is more appropriate

        current_measurements: str, not writeable
            returns the values for all current measurements divided by commas ','

        time_measurements: str, not writeable
            returns the values for all times in which measurements where taken divided by commas ','
    """
    __server_url = ""
    __address_space_name = "OPCUA_PLASMA_MEASUREMENTS_SERVER"
    __client = None
    __is_client_done = False

    current_list = []
    time_list = []
    voltage_list = []

    __address_space = None

    __selected_voltage_ramp = None
    __selected_voltage_sweep_time = None
    __selected_current_filter = None
    __selected_sensor_to_use = None
    __selected_gas = None
    __selected_magnetic_field = None

    __voltage_ramp = None
    __voltage_sweep_time = None
    __current_filter = None
    __sensor_to_use = None

    __abort_measurements = None
    __is_client_data_fully_sent = None
    __is_measurements_running = None
    __is_measurements_finished = None

    __current_measurements = None
    __time_measurements_ = None

    def __init__(self, server_url: str = "opc.tcp://127.0.0.1:9002"):
        """
        Initialize with server url
        Default url is set to local loopback address
        :param server_url: IP and Port to grab OPC-UA data from.
                           Format:  opc.tcp://[IP]:[PORT]
        """
        self.set_server_url(server_url)

    async def __initialize_client(self):
        """
        Initializes the client and all nodes that are handled by the server and used by the client
        :return: None
        """
        # OPC-UA server namespace to search for
        self.__address_space = await self.__client.get_namespace_index(self.__address_space_name)

        # assigns location to send measurement specifications and retrieve measurement data
        # from the selected OPC-UA server address space
        self.__voltage_ramp = await self.__client.nodes.root.get_child(
            ["0:Objects", f"{self.__address_space}:sensor", f"{self.__address_space}:voltage_ramp"])

        self.__voltage_sweep_time = await self.__client.nodes.root.get_child(
            ["0:Objects", f"{self.__address_space}:sensor", f"{self.__address_space}:voltage_sweep_time"])

        self.__current_filter = await self.__client.nodes.root.get_child(
            ["0:Objects", f"{self.__address_space}:sensor", f"{self.__address_space}:current_filter"])

        self.__sensor_to_use = await self.__client.nodes.root.get_child(
            ["0:Objects", f"{self.__address_space}:sensor", f"{self.__address_space}:sensor_to_use"])

        self.__abort_measurements = await self.__client.nodes.root.get_child(
            ["0:Objects", f"{self.__address_space}:sensor", f"{self.__address_space}:stop_measurements"])

        self.__is_client_data_fully_sent = await self.__client.nodes.root.get_child(
            ["0:Objects", f"{self.__address_space}:sensor", f"{self.__address_space}:is_client_data_fully_sent"])

        self.__is_measurements_running = await self.__client.nodes.root.get_child(
            ["0:Objects", f"{self.__address_space}:sensor", f"{self.__address_space}:is_measurements_running"])

        self.__is_measurements_finished = await self.__client.nodes.root.get_child(
            ["0:Objects", f"{self.__address_space}:sensor", f"{self.__address_space}:is_measurements_finished"])

        self.__current_measurements = await self.__client.nodes.root.get_child(
            ["0:Objects", f"{self.__address_space}:sensor", f"{self.__address_space}:current_measurements"])

        self.__time_measurements = await self.__client.nodes.root.get_child(
            ["0:Objects", f"{self.__address_space}:sensor", f"{self.__address_space}:time_measurements"])

    async def __send_measurement_parameters_to_server(self):
        """
        Sends the measurement parameters to the server
        :return: None
        """
        await self.__voltage_ramp.set_value(','.join(map(str, self.__selected_voltage_ramp)))
        await self.__voltage_sweep_time.set_value(self.__selected_voltage_sweep_time)
        await self.__current_filter.set_value(self.__selected_current_filter)
        await self.__sensor_to_use.set_value(self.__selected_sensor_to_use)
        await self.__is_client_data_fully_sent.set_value(True)

    async def __fix_current_and_time_data_types(self):
        """
        Fixes the data types of the current and time measurements nodes sent by the server.
        Changes them from strings to lists.

        NOTE: these nodes should be changed so this conversion is not needed
        :return: None
        """
        self.current_list = [float(x) for x in self.current_list if x != '']
        self.time_list = [datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f') for x in self.time_list]

    async def start_client(self):
        """
        Sends measurement data to server and awaits measurement data.
        Gets the server data asynchronously on server url.

        Requires to be called as an asyncio function

        :return: None
        """
        try:
            # starts server on specified server url
            async with Client(url=self.get_server_url()) as self.__client:

                await self.__initialize_client()

                print(f"CLIENT STARTED: client started on {self.get_server_url()}")

                self.__is_client_done = False

                # waits for server to be available to send data
                # TODO: add a timeout for this
                while not self.__is_client_done:

                    await asyncio.sleep(2)

                    # if server is not currently running measurements, runs our measurements
                    if not await self.__is_measurements_running.get_value():

                        await self.__send_measurement_parameters_to_server()

                        print(f"CLIENT AWAITING RESPONSE: client awaiting response from {self.get_server_url()}")

                        # waits for server to finish measurements
                        while True:
                            # Note: current list is translated to floats and times to datetime
                            self.current_list = (await self.__current_measurements.get_value()).split(',')
                            self.time_list = (await self.__time_measurements.get_value()).split(',')
                            await self.__fix_current_and_time_data_types()
                            print(f'Current Current:{self.current_list}')
                            print(f'Current Time: {self.time_list}')

                            # gets server data
                            if await self.__is_measurements_finished.get_value():
                                self.current_list = (await self.__current_measurements.get_value()).split(',')
                                self.time_list = (await self.__time_measurements.get_value()).split(',')
                                await self.__fix_current_and_time_data_types()
                                self.__is_client_done = True
                                break

                            # delay between each data read
                            await asyncio.sleep(2)

                        print(f"CLIENT RECEIVED DATA: client received data on {self.get_server_url()}")

        except WindowsError as e:
            print(f'CLIENT ERROR: {e} on {self.get_server_url()}')

    def set_measurement_parameters(self, voltage_ramp: list, voltage_sweep_time: float, sensor_to_use: str,
                                   gas: str = 'Air', magnetic_field: str = 'Cusp', current_filter: str = 'None'):
        """
        Sets the parameters to use for plasma measurements

        :param voltage_ramp: voltage ramp (list of voltages) to send to plasma sensor

        :param voltage_sweep_time: Wait time between measurements (in .1 seconds)

        :param sensor_to_use: Plasma sensor to use for measurements
                                Values: 'SLP', 'DLP', 'HEA'
                                SLP -> Single Langmuir Probe
                                DLP -> Double Langmuir Probe
                                HEA -> Hyperbolic Energy Analyzer

        :param gas: Gas used during plasma measurements
                                Values: 'Air'

        :param magnetic_field: magnetic field used during measurements

        :param current_filter: Data filter to apply to final list of current
                               Values: 'None' -> No filter applied
                                       'SOS' -> SOS filter
        :return: None
        """
        # FOUND ON CODE LINE 523 of 'SLPcontinuous'
        self.voltage_list = voltage_ramp

        self.__selected_voltage_ramp = voltage_ramp
        self.__selected_voltage_sweep_time = voltage_sweep_time
        self.__selected_sensor_to_use = sensor_to_use
        self.__selected_gas = gas
        self.__selected_current_filter = current_filter
        self.__selected_magnetic_field = magnetic_field

    def load_measurements_csv(self, filepath: str):
        """
        Reads the data on a specified csv file.
        Data will be stored as a sensor data list.

        :param filepath: filepath to read csv from
        :return: None
        """
        try:

            with open(filepath, 'r', newline='') as file:

                # csv reader
                reader = csv.DictReader(file, delimiter=',', quotechar='|')

                # verifies that the keys time, voltage, and current are present inside the csv
                if 'time' in reader.fieldnames and 'voltage' in reader.fieldnames and \
                        'current' in reader.fieldnames:

                    # appends rows to sensor data list
                    for row in reader:
                        self.voltage_list.append(row['voltage'])
                        self.current_list.append(row['current'])
                        self.time_list.append(row['time'])

                else:
                    raise (KeyError("csv key 'time', 'voltage', or 'current' not found"))

        except (FileNotFoundError, KeyError) as error:
            print(f'CLIENT ERROR: {error}')

    def stop_listening(self):
        """
        Stop listening for server data
        :return: None
        """
        print(f"CLIENT STOPPED LISTENING: client stopped listening on {self.get_server_url()}")
        self.__client.close_session()

    def set_server_url(self, server_url: str):
        """
            Change server url server will serve data on
            :param server_url:  IP and Port to grab OPC-UA data from.
                               Format:  opc.tcp://[IP]:[PORT]
            :return: None
        """
        self.__server_url = server_url

    def get_server_url(self):
        """
            Returns server url server will serve data on
            :return: IP and Port to grab OPC-UA data from.
                     Format:  opc.tcp://[IP]:[PORT]
            :rtype: str
        """
        return self.__server_url

    def get_sensor_used(self):
        """
        Gets the type of sensor used for plasma measurements
        :return: Plasma sensor to use for measurements
                                Values: 'SLP', 'DLP', 'HEA'
                                SLP -> Single Langmuir Probe
                                DLP -> Double Langmuir Probe
                                HEA -> Hyperbolic Energy Analyzer
        :rtype: str
        """
        return self.__selected_sensor_to_use

    def get_gas(self):
        """
        Gets the gas used for plasma measurements
        :return: gas used for measurements
        :rtype: str
        """
        return self.__selected_gas

    def get_magnetic_field(self):
        """
        Returns the magnetic field used during measurements
        :return:magnetic field used during measurements
        :rtype: str
        """
        return self.__selected_magnetic_field

    def get_voltage_list(self):
        """
        Returns list of voltages (these voltages act as the voltage ramp) passed onto the plasma sensor
        :return: voltage ramp
        :rtype: list
        """
        return self.voltage_list

    def get_current_list(self):
        """
        Returns calculated currents from the plasma sensor
        :return: current list from plasma sensor
        :rtype: list
        """
        return self.current_list

    def get_time_list(self):
        """
        Returns times at which the currents were calculated from the plasma sensor
        :return: times currents were calculated on plasma sensor
        :rtype: list
        """
        return self.time_list

    def is_client_done(self):
        """
        Returns true if the client has received all data for all measurements from the server
        :return: True if measurements are done, False if not
        :rtype: bool
        """
        return self.__is_client_done


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    client = DataClient()
    client.set_measurement_parameters([1, 2, 3, 4, 5], .5, 'SLP')

    asyncio.run(client.start_client())

    print(client.get_current_list())
    print(client.get_time_list())
