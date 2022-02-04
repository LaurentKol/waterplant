from datetime import datetime, timedelta
import statistics
import logging
from typing import List, Dict

from btlewrap.bluepy import BluepyBackend
from btlewrap.base import BluetoothBackendException
from miflora.miflora_poller import (MI_BATTERY, MI_CONDUCTIVITY, MI_LIGHT, MI_MOISTURE, MI_TEMPERATURE, MiFloraPoller)

from waterplant.config import config

#TODO: Create a Sensor class used by SensorsGroup
class SensorsGroup:
    def __init__(self, sensors: List[Dict]) -> None:
        self.sensor_pollers = {}
        self.last_battery_levels_checked = datetime.now()
        # Alternatively, for debugging, first battery check to not wait for config.check_battery_freq_days 
        # self.last_battery_levels_checked = datetime.now() - timedelta(days=config.check_battery_freq_days)
        for sensor in sensors:
            self.sensor_pollers[sensor['name']] = MiFloraPoller(sensor['mac'], BluepyBackend, cache_timeout=config.miflora_cache_timeout)

    def __repr__(self) -> str:
        return f'sensor group'
#        return f'{self.get_moisture()}'

    def get_moisture(self) -> int:
        moisture_measurements = []

        for sensor_name, sensor_poller in self.sensor_pollers.items():
            try:
                measurment = sensor_poller.parameter_value(MI_MOISTURE)
                logging.info(f'{sensor_name} moisture measurement: {measurment}')
                moisture_measurements.append(measurment)
            except BluetoothBackendException:
                logging.warn(f'Failed to read from {sensor_name}')

        if moisture_measurements:
            measurements_avg = statistics.mean(moisture_measurements)
            logging.info(f'Aggregate moisture measurements: {measurements_avg}')
        else:
            measurements_avg = None

        return measurements_avg

    def check_battery(self) -> dict:
        battery_levels = {}
        for sensor_name, sensor_poller in self.sensor_pollers.items():
            try:
                measurment = sensor_poller.parameter_value(MI_BATTERY)
                logging.info(f'{sensor_name} battery measurement: {measurment}')
                battery_levels[sensor_name] = measurment
                self.last_battery_levels_checked = datetime.now()
            except BluetoothBackendException:
                logging.warn(f'Failed to read from {sensor_name}')

        return battery_levels
