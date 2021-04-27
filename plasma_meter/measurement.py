from plasma_meter.sensor_data import SensorData


class Measurement:
    """
    Default data and methods for a base plasma sensor measurement

    Attributes:
    __________
    __sensor_data_list: List
        holds the sensor data for all instant times during a measurement

    Methods:
    -------
    append(self, sensor_data_list: list):
        appends a sensor data list to the sensor data list
    append(self, sensor_data: SensorData):
        appends a sensor data instance to the sensor data list
    remove(self, sensor_data_list: list):
        removes a sensor data list from the sensor data list
     remove(self, sensor_data: SensorData):
        removes a sensor data instance from the sensor data list
     get_sensor_data_list(self):
        returns the sensor data list
    """
    __sensor_data_list = None

    def __init__(self, sensor_data_list: list = []):
        self.__sensor_data_list = sensor_data_list

    def append(self, sensor_data_list: list):
        """
        Appends a sensor data list to the measurement data
        :param sensor_data_list: sensor data list to append
        :return: None
        """
        self.__sensor_data_list += sensor_data_list

    def append(self, sensor_data: SensorData):
        """
        Appends an instant of sensor data to the measurement data
        :param sensor_data: instance of sensor data for a period in time
        :return: None
        """
        self.__sensor_data_list.append(sensor_data)

    def remove(self, sensor_data_list: list):
        """
        Removes a sensor data list from measurement data
        :param sensor_data_list: sensor data list to remove
        :return: None
        """
        for sensor_data in sensor_data_list:

            # checks that the sensor data inside the list is actually a SensorData instance
            if isinstance(sensor_data, SensorData):
                sensor_data_list.remove(sensor_data)

    def remove(self, sensor_data: SensorData):
        """
        Removes an instant of sensor data from the measurement data
        :param sensor_data: instance of sensor data for a period in time
        :return: None
        """
        self.__sensor_data_list.remove(sensor_data)

    def get_sensor_data_list(self):
        """
        Returns all recorded data from a sensor during a measurement
        :return:sensor_data_list
        :rtype: list
        """
        return self.__sensor_data_list


class SLPMeasurement(Measurement):
    """
    Holds the data and methods for a Single Langmuir Probe (SLP) plasma measurement
    """
    __density = 0
    __temperature = 0
    __mean_free_path = 0
    __debye_length = 0
    __larmor_radius = 0
    __temperature_ev = 0
    __plasma_potential = 0
    __floating_potential = 0

    def __init__(self):
        super().__init__()

    def __calculate_density(self):
        pass

    def __calculate_temperature(self):
        pass

    def __calculate_mean_free_path(self):
        pass

    def __calculate_debye_length(self):
        pass

    def __calculate_larmor_radius(self):
        pass

    def __calculate_temperature_ev(self):
        pass

    def __calculate_plasma_potential(self):
        pass

    def __calculate_floating_potential(self):
        pass

    def get_density(self):
        return self.__density

    def get_temperature(self):
        return self.__temperature

    def get_mean_free_path(self):
        return self.__mean_free_path

    def get_debye_length(self):
        return self.__debye_length

    def get_larmor_radius(self):
        return self.__larmor_radius

    def get_temperature_ev(self):
        return self.__temperature_ev

    def get_plasma_potential(self):
        return self.__plasma_potential

    def get_floating_potential(self):
        return self.__floating_potential


class DLPMeasurement(Measurement):
    """
    Holds the data and methods for a Double Langmuir Probe (DLP) plasma measurement
    """


class HEAMeasurement(Measurement):
    """
    Holds the data and methods for a Hyperbolic Energy Analyzer (HEA) plasma measurement
    """



