import mysql.connector
import datetime
from plasma_meter.calculations import ICalculations, CalculationsSLP, CalculationsDLP, CalculationsHEA
from abc import abstractmethod, ABCMeta
import uuid

class IDatabaseManager:
    """
    Interface class for the Database Manager that takes the values from Calculations objects and stores them in the
    Plasma Meter database
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def insert_calculations(self, calculations: ICalculations):
        raise NotImplementedError()

    @abstractmethod
    def get_measurement(self, date_and_time: datetime.datetime):
        raise NotImplementedError()

    @abstractmethod
    def get_measurements_page(self, page: int):
        raise NotImplementedError()

    @abstractmethod
    def remove_measurement(self, date_and_time: datetime.datetime):
        raise NotImplementedError()


class DatabaseManager:
    """
    Manages the database for the Plasma Meter application

    Attributes:
    ----------
    __database: MySQLConnection
        MySQL connection to the database. Holds the IP and Port of the database
        and the default User and Password
    __database_cursor: Cursor
        Executes database queries

     Methods:
    ________
    insert_measurement(sensor_data_list: Measurement):
        inserts a measurement into the database
    retrieve_measurement(date_and_time: datetime):
        retrieves a measurement from the database

    """
    __database = None
    __database_cursor = None

    def __init__(self, host: str = 'localhost', port: int = 3306, \
                 user: str = 'root', password: str = 'P0pc@rn00'):
        """
        Initialize database IP, Port, User, and Password
        :param host: IP address of database
        :param port: Port of database connection
        :param user: user to connect to database with
        :param password: password of user to connect to databsae with
        """
        self.__database = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database='plasma_meter'
        )

        self.__database_cursor = self.__database.cursor()

    def __insert_calculations_SLP(self, calculations: CalculationsSLP):
        """
        Inserts Single Langmuir Probe (SLP) measurements into database
        :param calculations: calculations objects containing measurement variables
        :return: None
        """
        time = calculations.get_time_list()[-1].strftime('%Y-%m-%d %H:%M:%S')
        id = uuid.uuid5(namespace=uuid.NAMESPACE_DNS, name=time)

        self.__database_cursor.execute('INSERT INTO measurements (id, measurement_time, sensor_used, '
                                       'magnetic_field_used, gas_used) '+
                                       f'VALUES ("{id}", "{time}", "{calculations.get_sensor_used()}", '
                                       f'"{calculations.get_magnetic_field()}", "{calculations.get_gas_used()}")')

        self.__database_cursor.execute('INSERT INTO slp_measurements (id, floating_potential, plasma_potential, '
                                       'temperature, temperature_env, density, mean_free_path, debye_length, larmor_radius) '+
                                       f'VALUES ("{id}", "{calculations.get_floating_potential()}", '
                                       f'"{calculations.get_plasma_potential()}", "{calculations.get_temperature()}", '
                                       f'"{calculations.get_temperature_ev()}", "{calculations.get_density()}", '
                                       f'"{calculations.get_mean_free_path()}", "{calculations.get_debye_length()}", '
                                       f'"{calculations.get_larmor_radius()}")')
        self.__database.commit()

    def __insert_calculations_DLP(self, calculations: CalculationsDLP):
        """
        Inserts Double Langmuir Probe (DLP) measurements into database
        :param calculations: calculations objects containing measurement variables
        :return: None
        """
        self.__database_cursor.execute('')
        self.__database.commit()

    def __insert_calculations_HEA(self, calculations: CalculationsHEA):
        """
        Inserts Hyperbolic Energy Analyzer (HEA) measurements into database
        :param calculations: calculations objects containing measurement variables
        :return: None
        """
        self.__database_cursor.execute('')
        self.__database.commit()

    def insert_calculations(self, calculations: ICalculations):
        """
        Inserts calculations into database
        :param calculations: calculations objects containing measurement variables
        :return: None
        """

        # inserts calculations for the selected plasma sensor
        if isinstance(calculations, CalculationsSLP):
            self.__insert_calculations_SLP(calculations)

        elif isinstance(calculations, CalculationsDLP):
            self.__insert_calculations_DLP(calculations)

        elif isinstance(calculations, CalculationsHEA):
            self.__insert_calculations_HEA(calculations)

        else:
            raise ValueError('Calculations object not implemented in database insert function')

    def __get_measurement_SLP(self, datetime: str):
        """
        Grabs SLP measurement for a specific datetime.
        Is called by the get_measurement() method
        :param date_and_time: datetime of measurement
        :return: containing query data
        :rtype: dict
        """

        self.__database_cursor.execute(f'SELECT m.id, m.measurement_time, m.sensor_used, m.magnetic_field_used, '
                                       f'm.gas_used, slp.floating_potential, slp.plasma_potential, slp.temperature,'
                                       f'slp.temperature_env, slp.density, slp.mean_free_path, slp.debye_length, '
                                       f'slp.larmor_radius FROM measurements AS m INNER JOIN slp_measurements AS slp '
                                       f'ON m.id = slp.id WHERE m.measurement_time = "{datetime}"')
        result = self.__database_cursor.fetchall()

        result_dict = {'id': result[0][0], 'measurement_time': result[0][1], 'sensor_used': result[0][2],
                       'magnetic_field_used': result[0][3], 'gas_used': result[0][4], 'floating_potential': result[0][5],
                       'plasma_potential': result[0][6], 'temperature': result[0][7],'temperature_env': result[0][8],
                       'density': result[0][9], 'mean_free_path': result[0][10], 'debye_length': result[0][11],
                       'larmor_radius': result[0][12]}

        return result_dict

    def __get_measurement_DLP(self, datetime: str):
        """
        Grabs DLP measurement for a specific datetime.
        Is called by the get_measurement() method
        :param date_and_time: datetime of measurement
        :return: containing query data
        :rtype: dict
        """
        pass

    def __get_measurement_HEA(self, datetime: str):
        """
        Grabs HEA measurement for a specific datetime.
        Is called by the get_measurement() method
        :param date_and_time: datetime of measurement
        :return: containing query data
        :rtype: dict
        """
        pass

    def get_measurement(self, date_and_time: datetime.datetime):
        """
        Gets measurement for a specific datetime
        :param date_and_time: datetime of measurement
        :return: dictionary containing measurement information
        :rtype: dict
        """
        time = date_and_time.strftime('%Y-%m-%d %H:%M:%S')

        self.__database_cursor.execute(f'SELECT sensor_used FROM measurements WHERE measurement_time = "{time}"')
        sensor_used = self.__database_cursor.fetchall()

        sensor_used = sensor_used[0][0]
        result = None

        if sensor_used == 'SLP':
            result = self.__get_measurement_SLP(time)
        elif sensor_used == 'DLP':
            pass
        elif sensor_used == 'HEA':
            pass
        else:
            raise ValueError('Database Error: sensor used for retrieved measurement is invalid')

        return result

    def get_measurements_by_page(self, page: int):
        """
        Gets measurements from database by page.
        Every page displays 20 measurements.
        Earliest measurements are found in the latest page and the oldest in the last page
        :param page: measurements page to display
        :return: measurements for a page inside a list containing dictionaries
        :rtype: list (representing rows) containing dictionaries
        """
        self.__database_cursor.execute('SELECT id, measurement_time, sensor_used, magnetic_field_used, gas_used '
                                       f'FROM measurements ORDER BY measurement_time DESC LIMIT {page * 10}, 10')
        result = self.__database_cursor.fetchall()

        results_organized = []

        for row in result:
            results_organized.append({'id': row[0], 'measurement_time': row[1], 'sensor_used': row[2],
                                      'magnetic_field': row[3], 'gas_used': row[4]})

        return results_organized

    def get_all_measurements(self):
        """
        Retruns all measurements from the database
        :return: all measurements inside a list containing dictionaries
        :rtype: list (representing rows) containing dictionaries
        """
        self.__database_cursor.execute('SELECT id, measurement_time, sensor_used, magnetic_field_used, gas_used '
                                       f'FROM measurements ORDER BY measurement_time DESC')
        result = self.__database_cursor.fetchall()

        results_organized = []

        for row in result:
            results_organized.append({'id': row[0], 'measurement_time': row[1], 'sensor_used': row[2],
                                      'magnetic_field': row[3], 'gas_used': row[4]})

        return results_organized

    def get_all_SLP_measurements(self):
        """
        Returns all SLP measurements from the database.
        :return: all SLP meaurements inside a list containing dictionaries
        :rtype: list (representing rows) containing dictionaries
        """
        self.__database_cursor.execute(f'SELECT m.id, m.measurement_time, m.sensor_used, m.magnetic_field_used, '
                                       f'm.gas_used, slp.floating_potential, slp.plasma_potential, slp.temperature,'
                                       f'slp.temperature_env, slp.density, slp.mean_free_path, slp.debye_length, '
                                       f'slp.larmor_radius FROM measurements AS m INNER JOIN slp_measurements AS slp '
                                       f'ON m.id = slp.id ORDER BY measurement_time DESC')
        result = self.__database_cursor.fetchall()

        results_organized = []

        for row in result:
            results_organized.append({'id': row[0], 'measurement_time': row[1], 'sensor_used': row[2],
                                      'magnetic_field': row[3], 'gas_used': row[4], 'floating_potential': row[5],
                                      'plasma_potential': row[6], 'temperature': row[7], 'temperature_env': row[8],
                                      'density': row[9], 'mean_free_path': row[10], 'debye_length': row[11],
                                      'larmor_radius': row[12]})

        return results_organized

    def get_all_DLP_measurements(self):
        """
        Returns all DLP measurements from the database.
        :return: all DLP meaurements inside a list containing dictionaries
        :rtype: list (representing rows) containing dictionaries
        """
        pass

    def get_all_HEA_measurements(self):
        """
        Returns all DLP measurements from the database.
        :return: all DLP meaurements inside a list containing dictionaries
        :rtype: list (representing rows) containing dictionaries
        """
        pass


    def remove_measurement(self, date_and_time: datetime.datetime):
        """
        Removes measurement with specified datetime
        :param date_and_time: datetime of measurement to remove
        :return: None
        """
        self.__database_cursor.execute('')
        self.__database.commit()

    def test(self):
        self.__database_cursor.execute('USE test')
        self.__database_cursor.execute('INSERT INTO users ' +
                                      'VALUES ("Ricardo", 119372)')
        self.__database_cursor.execute('SELECT * FROM users')

        result = self.__database_cursor.fetchall()

        self.__database.commit()

        return result


if __name__ == '__main__':
    database = DatabaseManager(host='localhost', user="'root'", password='password')
    # host = '70.45.152.184' is the location of the pi