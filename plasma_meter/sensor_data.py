import datetime


class SensorData:
    """
    Sensor data from a sensor reading at an instance of time

     Attributes:
     __________
     __voltage: float
        voltage sensor contains at time of measurement
     __current: float
        current sensor contains at time of measurement
    __time: datetime
        time measurement was taken

    Methods:
    _______
    get_voltage():
        returns voltage
    get_current():
        returns current
    get_time()
        returns time
    """
    __voltage = float()
    __current = float()
    __time = None

    def __init__(self, voltage: float, current: float, time: datetime):
        self.__voltage = voltage
        self.__current = current
        self.__time = time

    def get_voltage(self):
        """
        Returns voltage of measurement
        :return: voltage
        :rtype: float
        """
        return self.__voltage

    def get_current(self):
        """
        Returns current of measurement
        :return: current
        :rtype: float
        """
        return self.__current

    def get_time(self):
        """
        Returns time of measurement
        :return: time
        :rtype: datetime
        """
        return self.__time

    def __str__(self):
        return f'voltage: {self.get_voltage()}, current: {self.get_current()}, time: {self.get_time()}'

    def __eq__(self, sensor_data):
        """
        Equals operator overload
        """

        if (self.get_voltage() == sensor_data.get_voltage() and \
                self.get_current() == sensor_data.get_current() and \
                self.get_time() == sensor_data.get_time()):
            return True

        else:
            return False

    def __getitem__(self, item):
        """
        Returns value for Sensor Data parameters ("voltage", "current", "time")
        :param item: key to be searched for
        :return: value for specified key
        :rtype: string
        """
        if item == 'voltage':
            return self.get_voltage()

        elif item == 'current':
            return self.get_current()

        elif item == 'time':
            return self.get_time()

        else:
            return 'Not Known'
