from plasma_meter.server import DataServer
from plasma_meter.client import DataClient
from plasma_meter.calculations import CalculationsFactory, ICalculations, CalculationsSLP, CalculationsDLP, \
    CalculationsHEA
from plasma_meter.database import DatabaseManager
import asyncio
import threading
import numpy as np
import time


def run_server():
    """
    Runs plasma server indefinitely
    :return: None
    """
    data_server = DataServer()
    data_server.start_server_task()

async def calculate_and_store_sensor_variables(client, real_time_signal, graph_signal):
    """
    Realizes calculations for a sensor using data gathered from OPC-UA client and graphs them
    :param client: OPC-UA client measurement  data was gathered from
    :return: None
    """

    while len(client.get_current_list()) < 4:
        await asyncio.sleep(1)
    calculations_factory = CalculationsFactory()
    calculations = calculations_factory.create_calculations(client)

    # calculates client values for the appropriate sensor
    while not client.is_client_done():
        calculations.calculate_all()

        send_signal(calculations, real_time_signal, graph_signal)

        print(calculations.__str__())

        await asyncio.sleep(2)

    # final calculation and finish
    calculations.calculate_all()
    calculations.save_to_csv()
    print(calculations.__str__())

    send_signal(calculations, real_time_signal, graph_signal)

    database = DatabaseManager(user="'root'", password='P0pc@rn00')
    database.insert_calculations(calculations)
    print(database.get_measurement(calculations.get_time_list()[-1]))
    print('-------------------DONE---------------------------')


def calculate_voltage_ramp(voltage_range_start: int, voltage_range_end: int, number_of_measurements: int):
    """
    Calculates voltage ramp to use on plasma sensor
    :param voltage_range_start: starting voltage for voltage ramp
    :param voltage_range_end: ending voltage for voltage ramp
    :param number_of_measurements: number of measurements to generate with plasma sensor
    :return: voltage ramp to send to plasma sensor
    :rtype: list
    """
    voltage_ramp = np.linspace(voltage_range_start, voltage_range_end, number_of_measurements)
    voltage_ramp = list(voltage_ramp)
    return voltage_ramp


async def run_measurements(voltage_range, voltage_sweep_time, number_of_measurements, sensor_to_use, gas,
                           real_time_signal, graph_signal):
    """
    Runs measurements and graphs them
    :param voltage_range: List specifying the minimum and maximum voltages to read from a plasma sensor.
                                Format: [10, 50] -> 10 is the minimum voltage and 50 the maximum voltage
    :param voltage_sweep_time: Wait time between measurements (in .1 seconds)
    :param number_of_measurements: number of measurements to perform
    :param sensor_to_use: Plasma sensor to use for measurements
                                Values: 'SLP', 'DLP', 'HEA'
                                SLP -> Single Langmuir Probe
                                DLP -> Double Langmuir Probe
                                HEA -> Hyperbolic Energy Analyzer
    :param gas: Gas used during plasma measurements
                                Values: 'Air'
    :return: None
    """

    # voltage ramp calculation
    voltage_ramp = calculate_voltage_ramp(voltage_range[0], voltage_range[1], number_of_measurements)

    # client setup
    client = DataClient()
    client.set_measurement_parameters(voltage_ramp, voltage_sweep_time, sensor_to_use)

    task1 = asyncio.create_task(client.start_client())
    task2 = asyncio.create_task(calculate_and_store_sensor_variables(client, real_time_signal, graph_signal))

    await task1
    await task2


def run_in_separate_thread(voltage_ramp, voltage_sweep_time, number_of_measurements, sensor_to_use, gas, real_time_signal, graph_signal):
    asyncio.run(run_measurements(voltage_ramp, voltage_sweep_time, number_of_measurements, sensor_to_use, gas, real_time_signal, graph_signal))

def send_signal(calculations, real_time_signal, graph_signal):
    voltage_list = calculations.get_voltage_list()
    current_list = calculations.get_current_list()
    time_list = calculations.get_time_list()
    floating_potential = calculations.get_floating_potential()
    plasma_potential = calculations.get_plasma_potential()
    temperature = calculations.get_temperature()
    temperature_ev = calculations.get_temperature_ev()
    density = calculations.get_density()
    mean_free_path = calculations.get_mean_free_path()
    debye_length = calculations.get_debye_length()
    larmor_radius = calculations.get_larmor_radius()

    real_time_signal.emit(debye_length, density, larmor_radius, temperature_ev, mean_free_path, temperature,
                          plasma_potential, floating_potential)
    graph_signal.emit(voltage_list, current_list)


if __name__ == '__main__':

    # run_instance = threading.Thread(target=run_in_separate_thread([-300, 300], .5, 300, 'SLP', 'Air'))
    # run_instance.start()
    start_time = time.time()

    asyncio.run(run_measurements([-300, 300], .05, 300, 'SLP', 'Air'))

    print(f'TIME ELAPSED:{time.time() - start_time}')
    # calculations = CalculationsSLP(None)
    # calculations.load_csv('SLP_measurements.csv')
    # print(calculations.__str__())
