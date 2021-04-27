from plasma_meter.server import DataServer
from plasma_meter.client import DataClient
from plasma_meter.database import DatabaseManager
from plasma_meter.measurement import Measurement, SLPMeasurement
from plasma_meter.sensor_data import SensorData
import time
import asyncio
import threading
import os
from plasma_meter.calculations import CalculationsFactory, CalculationsSLP, CalculationsDLP, CalculationsHEA
import numpy as np

def run_server():
    data_server = DataServer()
    data_server.start_server_task()


async def calculate(client):

    while len(client.get_current_list()) < 4:
        await asyncio.sleep(1)
    calculations_factory = CalculationsFactory()
    calculations = calculations_factory.create_calculations(client)

    # calculates client values for the appropriate sensor
    while not client.is_client_done():

        calculations.calculate_all()
        print(calculations.__str__())
        await asyncio.sleep(2)

    # final calculation and finish
    calculations.calculate_all()
    print(calculations.__str__())
    print('-------------------DONE---------------------------')


async def main():

    # making server thread
    server = threading.Thread(target=run_server)
    server.start()

    # voltages
    voltage_range = [-300, 300]
    number_of_measurements = 500

    voltage_ramp = np.linspace(voltage_range[0], voltage_range[1], number_of_measurements)
    voltage_ramp = list(voltage_ramp)

    # client setup
    client = DataClient()
    client.set_measurement_parameters(voltage_ramp, .5, sensor_to_use='SLP')

    task1 = asyncio.create_task(client.start_client())
    task2 = asyncio.create_task(calculate(client))

    await task1
    await task2

    # task2 = asyncio.ensure_future(calculate(client))

    # asyncio.run(client.start_client())

    # calculations_factory = CalculationsFactory()
    # calculations = calculations_factory.create_calculations(client)
    #
    # while not client.is_client_done():
    #     print("i got here you know")
    #     calculations.calculate_all()
    #     print(calculations.__str__())
    #
    # calculations.calculate_all()
    #
    # print(calculations.__str__())
    # print('DONE')



if __name__ == '__main__':
    asyncio.run(main())

    # loop = asyncio.new_event_loop()
    # loop.call_soon()
    # loop.run
