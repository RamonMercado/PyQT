# NOTE: asyncua uses the same methods used in the "opcua" python library, so most
# implementations using the "opcua" python library can be done in the "asyncua" library
from asyncua import Server
import asyncio
import logging
import datetime
import time

class DataServer:
    """
    OPC-UA Asynchronous Data Server

    NOTE: attributes that are specified in the format
          'Node, data_type' mean that the attribute is an OPC-UA
          node that holds the specified data type

    Attributes:
    ----------
    __server_url: str
        IP and Port to which the OPC-UA server will send data to.
        Format:  opc.tcp://[IP]:[PORT]
    __address_space_name: str
        OPC-UA server data address space name
    __server_name: str
        name of the OPC-UA server
    __server: Server
        asynchronous OPC-UA server

    __address_space: Node
        OPC-UA server address space
    __sensor: Node
        main objects that holds all variables shared by the server

    __voltage_ramp: Node, list
        list of voltages to apply to plasma sensor
    __voltage_sweep_time: Node, float
        wait time between measurements (in .1 seconds)
    __current_filter: Node, str
        Data filter to apply to final list of current
                               Values: 'None' -> No filter applied
                                       'SOS' -> SOS filter
    __sensor_to_use: Node, str
        Plasma sensor to use for measurements
                                Values: 'SLP', 'DLP', 'HEA'
                                SLP -> Single Langmuir Probe
                                DLP -> Double Langmuir Probe
                                HEA -> Hyperbolic Energy Analyzer

    __abort_measurements: Node, bool
        Signals the server to abort a measurement
    __is_client_data_fully_sent: Node, bool
        Client signal that it has finished sending measurement parameters
    __is_measurements_running: Node, bool
        Specifies if the server is running a measurement
    __is_measurements_finished: Node, bool
        Server signal that specifies that it has finished calculating measurements

    __current_measurements: Node, str
        Holds the calculated 'current' from the plasma sensor
    __time_measurements: Node, str
        Times in which the plasma sensor's current was calculated

    Methods:
    _______
    __initialize_server():
         Initializes the server and all nodes handled by the server
    __flush_measurement_parameters():
         Flushes the values of a measurement so conflicts can be avoided when doing new measurements
    __check_client_data_received():
        Checks if client data has been fully received

    __run_measurements():
         Runs measurements with entered measurement parameters
    __run_SLP_measurements():
        Runs measurements for a Single Langmuir Probe (SLP) plasma sensor
    __run_DLP_measurements():
        Runs measurements for a Double Langmuir Probe (DLP) plasma sensor
    __run_HEA_measurements():
        Runs measurements for a Hyperbolic Energy Analyzer (HEA) plasma sensor

    start_server():
        Awaits for a client connection and serves server data indefinitely
        and asynchronously to server url.
    start_server_task():
        Starts server synchronously (without using asyncio)
    close_server():
        Stops server from serving data
    stop_measurements():
        Signals the server to abort generating measurements

    set_server_url(server_url: str):
        Change server url to serve data on
    get_server_url():
        Returns server url to serve data on
    get_server_name():
        Returns server name

    Shares the following data with clients:
    --------------------------------------
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
    __server_name = "Plasma Meter Server"
    __server = None

    __address_space = None
    __sensor = None

    __voltage_ramp = None
    __voltage_sweep_time = None
    __current_filter = None
    __sensor_to_use = None

    __abort_measurements = None
    __is_client_data_fully_sent = None
    __is_measurements_running = None
    __is_measurements_finished = None

    __current_measurements = None
    __time_measurements = None

    def __init__(self, server_url: str = "opc.tcp://127.0.0.1:9002"):
        """
        Initialize with server url
        Default url is set to local loopback address
        :param server_url: IP and Port to which the OPC-UA server will send data to.
                           Format:  opc.tcp://[IP]:[PORT]
        """
        self.set_server_url(server_url)

    async def __initialize_server(self):
        """
        Initializes the server and all nodes handled by the server
        :return: None
        """
        # instantiates server
        self.__server = Server()
        await self.__server.init()
        self.__server.set_endpoint(self.get_server_url())
        self.__server.set_server_name(self.get_server_name())

        # sets server address space
        self.__address_space = await self.__server.register_namespace(self.__address_space_name)

        # sensor object
        self.__sensor = await self.__server.nodes.objects.add_object(self.__address_space, 'sensor')

        #  self.__sensor object variables (see method docstring for description of each)
        self.__voltage_ramp = await self.__sensor.add_variable(self.__address_space, "voltage_ramp", val='')
        self.__voltage_sweep_time = await self.__sensor.add_variable(self.__address_space, "voltage_sweep_time", 0.0)
        self.__current_filter = await self.__sensor.add_variable(self.__address_space, "current_filter", val='None')
        self.__sensor_to_use = await self.__sensor.add_variable(self.__address_space, "sensor_to_use", '')
        self.__abort_measurements = await self.__sensor.add_variable(self.__address_space, "stop_measurements", False)
        self.__is_client_data_fully_sent = await self.__sensor.add_variable(self.__address_space,
                                                                            "is_client_data_fully_sent", val=False)
        self. __is_measurements_running = await self.__sensor.add_variable(self.__address_space,
                                                                           "is_measurements_running", val=False)
        self.__is_measurements_finished = await self.__sensor.add_variable(self.__address_space,
                                                                           "is_measurements_finished", val=False)
        self.__current_measurements = await self.__sensor.add_variable(self.__address_space,
                                                                       "current_measurements", val='')
        self.__time_measurements = await self.__sensor.add_variable(self.__address_space,
                                                                    "time_measurements", val='')

        # makes the sensor object's variables that the client can modify writeable
        await self.__voltage_ramp.set_writable()
        await self.__voltage_sweep_time.set_writable()
        await self.__sensor_to_use.set_writable()
        await self.__abort_measurements.set_writable()
        await self.__is_client_data_fully_sent.set_writable()
        await self.__current_filter.set_writable()

    async def __flush_measurement_parameters(self):
        """
        Flushes the values of a measurement so conflicts can be avoided when doing new measurements
        :return: None
        """
        # flushes measurement parameters
        await self.__voltage_ramp.set_value('')
        await self.__voltage_sweep_time.set_value(0.0)
        await self.__sensor_to_use.set_value('')
        await self.__is_client_data_fully_sent.set_value(False)
        await self.__is_measurements_finished.set_value(False)
        await self.__abort_measurements.set_value(False)

    async def __check_client_data_received(self):
        """
        Checks if client data has been fully received
        :return:  True if client data has been fully received, false if not
        :rtype: bool
        """
        if await self.__is_client_data_fully_sent.get_value():
            return True
        else:
            return False

    async def __run_measurements(self):
        """
        Runs measurements with entered measurement parameters
        :return: None
        """

        await self.__is_measurements_running.set_value(True)

        # runs measurements for the selected plasma sensor
        if (await self.__sensor_to_use.get_value()) == 'SLP':
            await self.__run_SLP_measurements()

        elif (await self.__sensor_to_use.get_value()) == 'DLP':
            await self.__run_DLP_measurements()

        elif (await self.__sensor_to_use.get_value()) == 'HEA':
            await self.__run_HEA_measurements()

        else:
            print('SERVER ERROR: selected sensor not implemented')

        await self.__is_measurements_running.set_value(False)

    async def __run_SLP_measurements(self):
        """
        Runs measurements for a Single Langmuir Probe (SLP) plasma sensor
        :return: None
        """

        # variables to generate measurements
        measurement_voltage_sweep_time = await self.__voltage_sweep_time.get_value()
        measurement_voltage_ramp = await self.__voltage_ramp.get_value()
        number_of_measurements = float(len(measurement_voltage_ramp))
        step_time = float(measurement_voltage_sweep_time) / number_of_measurements
        current_filter = await self.__current_filter.get_value()

        # current sensing resistor of the Single Langmuir Probe
        shunt_resistor = 200.0

        # holds the generated current and time values
        calculated_current_measurements = ''
        calculated_time_measurements = ''

        voltages = [float(v) for v in (await self.__voltage_ramp.get_value()).split(',')]

        # runs measurements with no current filter
        if current_filter == 'None':

            # does measurements for each voltage
            for voltage in voltages:

                # stop measurements if abort flag is raised
                if await self.__abort_measurements.get_value():
                    break

                # NOTE: voltage must be sent to sensor before retrieving the current\
                # NOTE: time.sleep was used instead of asyncio.sleep to preserve miliseconds needed for runtime
                await asyncio.sleep(step_time)

                current = (voltage * -2.0) / shunt_resistor
                # print(time.time())

                # appends new current and time measurements
                # NOTE: join was used instead of string concatenation to preserve real time speed of application
                calculated_current_measurements = ''.join((calculated_current_measurements, str(current), ','))
                calculated_time_measurements = ''.join((calculated_time_measurements, str(datetime.datetime.now()), ','))

                # continuously updates current and time values
                await self.__current_measurements.set_value(calculated_current_measurements[:-1])
                await self.__time_measurements.set_value(calculated_time_measurements[:-1])

        # uses SOS filter for current
        elif current_filter == 'SOS':

            # does measurements for each voltage
            for voltage in voltages.split(','):

                # stop measurements if abort flag is raised
                if await self.__abort_measurements.get_value():
                    break

                # NOTE: voltage must be sent to sensor before retrieving the current
                await asyncio.sleep(step_time)

                current = (float(voltage) * 2.0) / shunt_resistor

                # appends new current and time measurements
                calculated_current_measurements += str(current) + ','
                calculated_time_measurements += str(datetime.datetime.now()) + ','

                # continuously updates current and time values
                await self.__current_measurements.set_value(calculated_current_measurements[:-1])
                await self.__time_measurements.set_value(calculated_time_measurements[:-1])

        else:
            print(f'SERVER ERROR: current filter not properly specified. If none is used, please select "None"')

        print(f'the current is {calculated_current_measurements}')
        print(f'the time is {calculated_time_measurements}')

        # transmits calculated data
        await self.__current_measurements.set_value(calculated_current_measurements[:-1])
        await self.__time_measurements.set_value(calculated_time_measurements[:-1])
        await self.__is_measurements_finished.set_value(True)

        print(f"SERVER RESULT TRANSMITTING: server transmitting data result on {self.get_server_url()}")
        await asyncio.sleep(10)

    async def __run_DLP_measurements(self):
        """
        Runs measurements for a Double Langmuir Probe (DLP) plasma sensor
        :return: None
        """
        pass

    async def __run_HEA_measurements(self):
        """
        Runs measurements for a Hyperbolic Energy Analyzer (HEA) plasma sensor
        :return: None
        """
        pass

    async def start_server(self):
        """
        Awaits for a client connection and serves server data indefinitely
        and asynchronously to server url.

        Requires to be called as an asyncio function

        Requires voltage_ramp, voltage_sweep_time, sensor_to_use, and client_data_fully_sent to be
        sent by client to run

        :return: None
        """
        await self.__initialize_server()

        # transmits that server is open to receive data
        print(f"SERVER STARTED: server open at {self.get_server_url()}")
        async with self.__server:

            # waits to receive server data
            while True:

                # print('SERVER STILL AWAITING')

                # client data received and measurements can start
                if await self.__check_client_data_received():

                    print(f"SERVER DATA RECEIVED: server received measurement data on {self.get_server_url()}")
                    await self.__run_measurements()

                    # flushes parameters after measurements have finished
                    await self.__flush_measurement_parameters()

                # delay for server to check for data changes
                await asyncio.sleep(2)

    def start_server_task(self):
        """
        Starts server synchronously (without using asyncio)
        :return: None
        """
        asyncio.run(self.start_server())

    async def close_server(self):
        """
        Stops server from serving data
        :return: None
        """
        print(f"CLOSE SERVER: closing server at {self.get_server_url()}")
        await self.__server.stop()

    async def stop_measurements(self):
        """
        Signals the server to abort generating measurements
        :return: None
        """
        # aborts measurements if measurements are running
        if await self.__is_measurements_running.get_value():
            await self.__abort_measurements.set_value(True)
        else:
            print("SERVER ERROR: measurements couldn't be stopped as no measurement is running")

    def set_server_url(self, server_url: str):
        """
        Change server url to serve data on
        :param server_url: IP and Port to which the OPC-UA server will send data to.
                           Format:  opc.tcp://[IP]:[PORT]
        :return: None
        """
        self.__server_url = server_url

    def get_server_url(self):
        """
        Returns server url to serve data on
        :return: IP and Port to which the OPC-UA server will send data to.
                 Format:  opc.tcp://[IP]:[PORT]
        :rtype: str
        """
        return self.__server_url

    def get_server_name(self):
        """
        Returns server name
        :return: string name of server
        :rtype: str
        """
        return self.__server_name


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)

    server = DataServer()

    asyncio.run(server.start_server())
    # can also be run with: server.start_server_task()
