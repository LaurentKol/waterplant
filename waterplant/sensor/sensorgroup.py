import logging
import statistics
from typing import List, Optional
import importlib
from datetime import datetime, timedelta

from waterplant.config import config
from .basesensor import BaseSensor

class SensorsGroup:
    def __init__(self, name: str, sensors: List[BaseSensor]) -> None:
        self.name = name
        self.last_battery_levels_checked = datetime.now() - timedelta(hours=config.check_battery_freq_hours)
        self.sensors = []
        for sensor in sensors:
            # Load the class named ${type}Sensor, if type is Miflora then MifloraSensor from miflorasensor.py
            SensorClass = getattr(importlib.import_module(f"waterplant.sensor.{sensor.type.lower()}sensor"), f'{sensor.type}Sensor')
            self.sensors.append(SensorClass(**sensor))

    def __repr__(self) -> str:
        return f'{self.sensors}'

    def get_moisture(self) -> Optional[int]:
        moisture_measurements = {}

        for sensor in self.sensors:
            if (measurement := sensor.get_moisture()):
                moisture_measurements.update({sensor.name: measurement})

        if moisture_measurements:
            measurements_avg = statistics.mean(moisture_measurements.values())
            logging.debug(f'Aggregate moisture measurements: {measurements_avg}')
            moisture_measurements.update({'average': measurements_avg})
            return moisture_measurements
        else:
            return None

    def get_measurements(self, sensor_types: List[str]) -> dict:
        """ Returns e.g: {'average': 220, 'light':{'balcony1a': 200, ... }, 'temperature': { ... }}
        Might also return partial list of sensor_types in case all sensors of a type are unavailable
        """
        measurements = {}

        for sensor_type in sensor_types:
            measurements[sensor_type] = {}

            for sensor in self.sensors:
                if (measurement := sensor.get_measurement(sensor_type)):
                    logging.debug(f'measurement: {measurement}')
                    measurements[sensor_type].update({sensor.name: measurement})

            if sensor_type in measurements and measurements[sensor_type]:
                logging.debug(f'measurements[sensor_type].values(): {measurements[sensor_type].values()}')
                sensor_measurements_avg = statistics.mean(measurements[sensor_type].values())
                logging.debug(f'Aggregate {sensor_type} measurements: {sensor_measurements_avg}')
                measurements[sensor_type].update({'average': sensor_measurements_avg})

        return measurements

    def get_battery(self) -> Optional[int]:
        battery_levels = {}

        for sensor in self.sensors:
            if (measurement := sensor.get_battery()):
                battery_levels.update({sensor.name: measurement})

        logging.info(f'Sensors battery are: {battery_levels}')
        return battery_levels
