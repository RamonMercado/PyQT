from abc import abstractmethod, ABCMeta
from plasma_meter.client import DataClient
import math
import numpy as np
from scipy import constants
import csv
from numba import jit
from numba.experimental import jitclass

class CalculationsFactory:
    """
    Factory design pattern class for calculations.
    """

    @staticmethod
    def create_calculations(client: DataClient):
        """
        Crates a calculation instance for the appropriate plasma sensor
        :param client: client used for plasma measurements
        :return: calculations object for the selected sensor
        """

        sensor_used = client.get_sensor_used()

        if sensor_used is None:
            raise ValueError('Sensor not selected in client')

        elif sensor_used == 'SLP':
            return CalculationsSLP(client)

        elif sensor_used == 'DLP':
            return CalculationsDLP(client)

        elif sensor_used == 'HEA':
            return CalculationsHEA(client)

        else:
            raise ValueError('Invalid Sensor selected in client')

    @staticmethod
    def create_calculations_str(sensor_used: str):
        """
        Crates a calculation class for the appropriate plasma sensor
        :param sensor_used: sensor used for measurements
        :return: calculations object for the selected sensor
        """

        if sensor_used is None:
            raise ValueError('Sensor not selected in client')

        elif sensor_used == 'SLP':
            return CalculationsSLP()

        elif sensor_used == 'DLP':
            return CalculationsDLP()

        elif sensor_used == 'HEA':
            return CalculationsHEA()

        else:
            raise ValueError(f'Invalid Sensor selected in client: {sensor_used} type: {type(sensor_used)}')


class ICalculations:
    """
    Interface for sensor calculations that can be calculated as DataClient is still receiving
    measurement data from the DataServer
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_all(self):
        raise NotImplementedError()

    @abstractmethod
    def link_with_client(self, client: DataClient):
        raise NotImplementedError()

    @abstractmethod
    def is_linked_to_client(self):
        raise NotImplementedError()

    @abstractmethod
    def save_to_csv(self, filename: str):
        raise NotImplementedError()

    @abstractmethod
    def save_to_database(self):
        raise NotImplementedError()

class CalculationsSLP(ICalculations):
    """
    Calculates and stores all calculable variables for a SLP (Single Langmuir Probe)

    Attributes:
    __________
    __density: flaot
        density of the plasma
    __temperature: float
        temperature of the plasma
    #TODO: what examctly does ev represent?
    __temperature_ev: float
        temperature ev of the plasma
    __mean_free_path: float
        mean free path of the plasma
    __debye_length: float
        debye length of the plasma
    __larmor_radius: float
        larmor radius of the plasma
    __plasma_potential: float
        plasma potential of the plasma
    __floating_potential: float
        floating potential of the plasma

    __voltage: list
        voltage ramp used in plasma sensor
    __current: list
        currents retrieved from plasma sensor
    __time: list
        times which currents were retrieved from plasma sensor
    __gas: str
        gas used for plasma measurements
    __magnetic_field: str
        magnetic field used during experiments
    __sensor_used: str
        sensor used for plasma measurements

    Methods:
    ________
    __get_current_voltage_derivative(self):
         Returns the derivative of the current over the derivative of the voltage for the full measurement
    __get_normalized_list(values_to_normalize: list):
         Normalizes a list of values

    __recopy_client_data(self):
        Copies current measurements data from client

    __calculate_density(self):
       calculates the desnity of a measurement
    __calculate_temperatures(self):
       calculates the temperature and temperature eV of a measurement
    __calculate_mean_free_path(self):
       calculates the mean free path of a measurement
    __calculate_debye_length(self):
       Calculates the Debye length of a measurement
    __calculate_larmor_radius(self):
       Calculates the Larmor radius of a measurement
    __calculate_plasma_potential(self):
       Calculates the plasma potential of a measurement
    __calculate_floating_potential(self):
       Calculates the floating potential of a measurement

    calculate_all(self):
        Calculates all variables for the SLP (Single Langmuir Probe
    link_with_client(self, client: DataClient):
        Links calculations object with a client instance
    is_linked_to_client(self):
        Asserts if Calculations class is linked with a data client
    save_to_csv(self, filename: str):
        Saves measurement data to a csv file
    save_to_database(self):
        Saves measurement data to Plasma Meter database

    get_current_list(self):
        Returns currents retrieved from plasma sensor
    get_voltage_list(self):
        Returns voltage ramp used for plasma measurements
    get_time_list(self):
        Returns the times which currents were retrieved from plasma sensor
    get_sensor_used(self):
        Gets the type of sensor used for plasma measurements
    get_gas_used(self):
        Returns gas used for plasma measurements
    get_magnetic_field(self):
        Returns the magnetic field used during measurements

    get_density(self):
        Returns the density of the full measurement
    get_temperature(self):
        Returns the temperature of the full measurement
    get_mean_free_path(self):
        Returns the mean free path of the full measurement
    get_debye_length(self):
        Returns the Debye length of the full measurement
    get_larmor_radius(self):
        Returns the Larmor radius of the full measurement
    get_temperature_ev(self):
        Returns the electron temperature of the full measurement
        NOTE: is this really the electron temperature?
    get_plasma_potential(self):
         Returns the plasma potential of the full measurement
    get_floating_potential(self):
        Returns the floating potential of the full measurement
    """
    __density = 0.0
    __temperature = 0.0
    __temperature_ev = 0.0
    __mean_free_path = 0.0
    __debye_length = 0.0
    __larmor_radius = 0.0
    __plasma_potential = 0.0
    __floating_potential = 0.0

    __client = None
    __voltage = None
    __current = None
    __time = None
    __gas = ''
    __magnetic_field = ''
    __sensor_used = ''

    def __init__(self, client: DataClient = None):

        if client is not None:
            self.__client = client
            self.__voltage = client.get_voltage_list().copy()
            self.__current = client.get_current_list().copy()
            self.__time = client.get_time_list().copy()
            self.__gas = client.get_gas()
            self.__magnetic_field = client.get_magnetic_field()
            self.__sensor_used = client.get_sensor_used()
        else:
            self.__voltage = []
            self.__current = []

    @staticmethod
    def __get_normalized_list(values_to_normalize: list):
        """
        Normalizes a list of values
        :param values_to_normalize: list of value to normalize
        :return: normalized list of values
        :rtype: list
        """
        normalized = values_to_normalize / np.max(values_to_normalize)
        return normalized

    def __get_current_voltage_derivative(self):
        """
        Returns the derivative of the current over the derivative of the voltage for the full measurement
        :return: derivative of current over derivative of voltage
        :rtype: list
        """
        derivative = np.diff(self.get_current_list()) / np.diff(self.get_voltage_list()[0:len(
            self.get_current_list())])

        return derivative

    def __recopy_client_data(self):
        """
        Copies current measurements data from client
        :return: None
        """
        self.__voltage = self.__client.get_voltage_list().copy()
        self.__current = self.__client.get_current_list().copy()
        self.__time = self.__client.get_time_list().copy()
        self.__gas = self.__client.get_gas()
        self.__magnetic_field = self.__client.get_magnetic_field()
        self.__sensor_used = self.__client.get_sensor_used()

    def __calculate_floating_potential(self):
        """
       Calculates the floating potential of a measurement
       :return: None

       Developer Notes:
       ---------------
       represented as vF in the old plasma app code
       found on line 714 of 'SLPcontinuous'
       """
        current = np.array(self.get_current_list())

        if len(np.argwhere(current < 0)) > 0:
            floating_potential_index = np.argwhere(current < 0)[-1].astype(int)[0]

            # sets new floating potential if the floating potential index is not out of range
            if floating_potential_index < len(current):
                self.__floating_potential = self.get_voltage_list()[floating_potential_index]

            else:
                pass
        else:
            pass

    def __calculate_plasma_potential(self):
        """
        Calculates the plasma potential of a measurement
        :return: None

        Developer Notes:
        ---------------
        This function is found on line 707 of the original code
        Plasma potential's represented as 'vp' and I think it's vp[0] that actually holds the value for
        the plasma potential
        645 dI_dVFiltered might show the way -> is calculated in the 'def Derivative'
        396 he used the signal library inside the FilterSignal method to filter the current
        """
        # this line was not used in SLPcontinuous
        # current_normalized = self.__get_normalized_list(values_to_normalize=self.__get_current_list())

        derivative_normalized = self.__get_normalized_list(self.__get_current_voltage_derivative())

        # this might contain a lot of redundancy (this is a direct copy from 'SLPcontinuous' on line
        max_derivative_index = np.argwhere(derivative_normalized == np.max(derivative_normalized)).astype(int)[0][0]

        self.__plasma_potential = self.get_voltage_list()[max_derivative_index]

    def __calculate_temperatures(self):
        """
        Calculates the temperature and temperature eV of a measurement
        :return: None

        Developer Notes:
        ---------------
        plasma potential (vP) = (VoltageSLP[index_di_max], index_di_max)
        this was found on code line 709
        voltageSLP is an attribute from the Another Window class
        voltageSLP is a list containing all voltages for a measurement
        NOTE: The original code used the index from the maximum index of the derivative of the current,
        but I don't see this being needed
        """

        # floating potential must be calculated so temperature can be calculated
        if self.get_floating_potential() == 0.0:
            self.__calculate_floating_potential()

        # plasma potential must be calculated so temperature can be calculated
        if self.get_plasma_potential() == 0.0:
            self.__calculate_plasma_potential()

        # gets middle index of the voltage list
        middle_index_voltage = int((len(self.get_voltage_list()) - 1) / 2)
        middle_index_current = int((len(self.get_current_list()) - 1) / 2)

        middle_voltage = self.get_voltage_list()[middle_index_voltage]

        # natural logarithm of current at middle position (middle index)
        middle_current_natural_log = np.log(self.get_current_list()[middle_index_current])

        # natural logarithm of current at highest position (highest index)
        max_current_natural_log = np.log(abs(self.get_current_list()[-1]))

        slope = (max_current_natural_log - middle_current_natural_log) / (self.get_plasma_potential() - middle_voltage)

        # calculates temperature values
        self.__temperature = -1 * math.e / slope
        self.__temperature_ev = 1

    def __calculate_density(self):
        """
        Calculates the density of a measurement
        :return: None

        Developer Notes:
        ---------------
        constants.electron_mass = 9.1093837015e-31

        I_vp is current at the maximum index of the derivative of the current
        I_vp = current[max_index_of_derivative_of_current] , not sure what they meant by this
        like in temperature, I will assume that we can just use the highest current
        NOTE: The original code used the index from the maximum index of the derivative of the current,
        but I don't see this being needed
        """

        # directly fetched this value from the old plasma app code
        area = 30.3858e-06

        # print(f'top dividy boi:{self.get_temperature_ev() * abs(math.e)}')

        # calculates the density
        voltage_over_current_derivative_normalized = self.__get_normalized_list(self.__get_current_voltage_derivative())

        max_current_derivative_index = np.argwhere(voltage_over_current_derivative_normalized ==
                                                   np.max(voltage_over_current_derivative_normalized)).astype(int)[0][0]

        self.__density = -1 * self.get_current_list()[max_current_derivative_index] / (
                math.e * area * math.sqrt(self.get_temperature_ev() * abs(math.e) / (2.0 * math.pi *
                                                                                         constants.electron_mass)))

    def __calculate_mean_free_path(self):
        """
        Calculates the mean free path of a measurement
        :return: None

        Developer Notes:
        ---------------
        3.4e18 seems to be the density of electrons in copper wires (idk)
        """

        # temperature ev must be calculated before calculating mean free path
        if self.get_temperature_ev() == 0.0:
            self.__calculate_temperatures()

        # density must be calculated before calculating mean free path
        if self.get_density() == 0.0:
            self.__calculate_density()

        # NOTE: this variable is "Zi" inside the 'slpShowParameters' old plasma app code. I am not sure if it represents electrical
        # impedance
        electrical_impedance = 0

        # electrical impedance value depends on gas used
        if self.get_gas_used() == 'air':
            electrical_impedance = 18

        else:
            electrical_impedance = 180

        # this equation is found on line 454 of the "slpShowParameters" old plasma app code
        mean_free_path = 3.4e18 * (self.get_temperature_ev() ** 2 / (electrical_impedance * self.get_density()))

        self.__mean_free_path = mean_free_path

    def __calculate_debye_length(self):
        """
        Calculates the Debye length of a measurement
        :return: None

        Developer Notes:
        ---------------
        """

        # density must be calculated before calculating debye length
        if self.get_density() == 0.0:
            self.__calculate_density()

        # epsilon_0 = eo, vacuum permittivity
        self.__debye_length = math.sqrt(
            abs(constants.epsilon_0 * self.get_temperature() / (self.get_density() * math.e ** 2)))

    def __calculate_larmor_radius(self):
        """
        Calculates the Larmor radius of a measurement
        :return: None

        Developer Notes:
        ---------------
        This function is found on line 695 of the original code
        """

        # he has an if B == 0 and then an else, but in his code B
        # was always 0
        if True:
            # This is the one that had the whole B = 0 and then if B == 0 thing
            self.__larmor_radius = -1

        else:
            B = 0  # idk what B is, but it's found above area on code line 738
            self.__larmor_radius = 3.37e-4 * (math.sqrt(self.get_temperature_ev())) / B

    def calculate_all(self):
        """
        Calculates all variables for the SLP (Single Langmuir Probe
        :return: None
        """
        # must contain a voltage list and a current list to calculate
        if self.is_linked_to_client() or self.has_voltage_and_current_lists():

            # recopies client information if it is connected to a client
            if self.is_linked_to_client():
                self.__recopy_client_data()

            self.__calculate_floating_potential()
            self.__calculate_plasma_potential()
            self.__calculate_temperatures()
            self.__calculate_density()
            self.__calculate_mean_free_path()
            self.__calculate_debye_length()
            self.__calculate_larmor_radius()

        else:
            raise ValueError('Calculations object not linked to a client')

    def link_with_client(self, client: DataClient):
        """
        Links client to get measurements data from
        :param client: client to extract
        :return: None
        """
        self.__client = client

    def is_linked_to_client(self):
        """
        Asserts if Calculations class is linked with a data client
        :return: True if is linked with data client, False if not
        :rtype: bool
        """
        if self.__client is None:
            return False

        else:
            return True

    def has_voltage_and_current_lists(self):
        """
        Asserts if the voltage list and current list are not empty and contain at least 3 elements each
        :return: True if voltage list and current list have at least 3 elements, False if not
        :rtype: bool
        """
        if len(self.__voltage) > 2 and len(self.__current) > 2:
            return True
        else:
            return False

    def load_csv(self, filename: str = 'SLP_measurements.csv'):
        """
        Loads measurement data from csv
        :param filename: Name of the file to get data from
                         if not specified, is saved to [probe name]_measurements.csv
        :return: None
        """
        data = []
        with open(filename, 'r') as file:

            reader = csv.DictReader(file)
            data = list(reader)[-1]

            self.__density = data['Density']
            self.__temperature = data['Temperature']
            self.__temperature_ev = data['Temperature ev']
            self.__mean_free_path = data['Mean Free Path']
            self.__debye_length = data['Debye Length']
            self.__larmor_radius = data['Larmor Radius']
            self.__plasma_potential = data['Plasma Potential']
            self.__floating_potential = data['Floating Potential']

    def load_csv_voltage_current(self, filename: str = 'SLP_meaurements_old.csv'):
        """
        Loads measurement data from csv that contains a list of voltages and a list of currents
        :param filename: Name of the file to get data from
        :return: None
        """

        with open(filename, 'r') as file:
            reader = csv.DictReader(file)

            for row in reader:
                self.__voltage.append(float(row['Voltage']))
                self.__current.append(float(row['Current']))

    def save_to_csv(self, filename: str = 'SLP_measurements.csv'):
        """
        Saves measurement data to a csv file
        :param filename: Name of the file to save data to
                         if not specified, is saved to [probe name]_measurements.csv
        :return: None
        """
        fields = ['DateTime', 'Density', 'Temperature', 'Temperature ev', 'Mean Free Path',
                  'Debye Length', 'Larmor Radius', 'Plasma Potential', 'Floating Potential']

        rows = [self.__time[0], self.get_density(), self.get_temperature(),
                self.get_temperature_ev(), self.get_mean_free_path(), self.get_debye_length(),
                self.get_larmor_radius(), self.get_plasma_potential(), self.get_floating_potential()]

        with open(filename, 'a') as file:

            # if file is empty, writes headers
            if file.tell() == 0:
                write = csv.writer(file)
                write.writerow(fields)
                write.writerow(rows)

            else:
                write = csv.writer(file)
                write.writerow(rows)

    def save_to_database(self):
        """
        Saves measurement data to Plasma Meter database
        :return: None
        """
        pass

    
    def get_current_list(self):
        """
        Returns currents retrieved from plasma sensor
        :return: currents from plasma sensor
        :rtype: list
        """
        return self.__current

    def get_voltage_list(self):
        """
        Returns voltage ramp used for plasma measurements
        :return: voltage ramp used in plasma sensor
        :rtype: list
        """
        return self.__voltage

    def get_time_list(self):
        """
        Returns the times which currents were retrieved from plasma sensor
        :return: times which currents were retrieved from plasma sensor
        :rtype: list
        """
        return self.__time

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
        return self.__sensor_used

    def get_gas_used(self):
        """
        Returns gas used for plasma measurements
        :return: gas used for plasma measurements
        :rtype: str
        """
        return self.__gas

    def get_magnetic_field(self):
        """
        Returns the magnetic field used during measurements
        :return:magnetic field used during measurements
        :rtype: str
        """
        return self.__magnetic_field

    def get_density(self):
        """
        Returns the density of the full measurement
        :return: density of the full measurement
        :rtype: float
        """
        return self.__density

    def get_temperature(self):
        """
        Returns the temperature of the full measurement
        :return: temperature of the full measurement
        :rtype: float
        """

        return self.__temperature

    def get_mean_free_path(self):
        """
        Returns the mean free path of the full measurement
        :return: mean free path of the full measurement
        :rtype: float
        """
        return self.__mean_free_path

    def get_debye_length(self):
        """
        Returns the Debye length of the full measurement
        :return: Debye length of the full measurement
        :rtype: float
        """
        return self.__debye_length

    def get_larmor_radius(self):
        """
        Returns the Larmor radius of the full measurement
        :return: Larmor radius of the full measurement
        :rtype: float
        """
        return self.__larmor_radius

    def get_temperature_ev(self):
        """
        Returns the electron temperature of the full measurement
        NOTE: is this really the electron temperature?
        :return: Electron temperature of the full measurement
        :rtype: float
        """
        return self.__temperature_ev

    def get_plasma_potential(self):
        """
        Returns the plasma potential of the full measurement
        :return: plasma potential of the full measurement
        :rtype: float
        """
        return self.__plasma_potential

    def get_floating_potential(self):
        """
        Returns the floating potential of the full measurement
        :return: floating potential of the full measurement
        :rtype: float
        """
        return self.__floating_potential

    def __str__(self):
        output = f'floating potential: {self.get_floating_potential()}\n' + \
                 f'plasma potential:   {self.get_plasma_potential()}\n' + \
                 f'temperature:        {self.get_temperature()}\n' + \
                 f'temperature ev:     {self.get_temperature_ev()}\n' + \
                 f'density:            {self.get_density()}\n' + \
                 f'mean free path:     {self.get_mean_free_path()}\n' + \
                 f'debye length:       {self.get_debye_length()}\n' + \
                 f'larmor radius:      {self.get_larmor_radius()}\n'
        return output


class CalculationsDLP(ICalculations):
    """
    Calculates and stores all calculable variables for a SLP (Single Langmuir Probe)
    """

    __data_client = None

    def __init__(self, client: DataClient):
        self.__data_client = client


class CalculationsHEA(ICalculations):
    """
    Calculates and stores all calculable variables for a SLP (Single Langmuir Probe)
    """

    __data_client = None

    def __init__(self, client: DataClient):
        self.__data_client = client
