import logging
import statistics
from typing import List, Optional
import importlib
from datetime import datetime, timedelta

from waterplant.config import config
from waterplant.homeassistant import hahelper
from .basesensor import BaseSensor

class SensorsGroup:
    def __init__(self, pot_name: str, sensors: List[BaseSensor]) -> None:
        self.pot_name = pot_name
        self.sensors = []
        self.moisture = None
        self.moisture_last_measurement = datetime.min
        for sensor in sensors:
            # Load the class named ${type}Sensor, if type is Miflora then MifloraSensor from miflorasensor.py
            SensorClass = getattr(importlib.import_module(f"waterplant.sensor.{sensor.type.lower()}sensor"), f'{sensor.type}Sensor')
            self.sensors.append(SensorClass(**sensor))

    def __repr__(self) -> str:
        return f'{self.sensors}'

    def get_measurements(self, sensor_types: List[str]) -> dict:
        """ Returns e.g: {'temperature': {'balcony4a': 8.1, 'balcony4b': 8.1, 'average': 8.1}, 'moisture': {'balcony4a': 14, 'balcony4b': 4, 'average': 9}}
        Might also return partial list of sensor_types in case all sensors of a type are unavailable
        """
        measurements = {}

        for sensor_type in sensor_types:
            measurements[sensor_type] = {}

            for sensor in self.sensors:
                if (measurement := sensor.get_measurement(sensor_type)):
                    measurements[sensor_type].update({sensor.name: measurement})

                    if config.homeassistant.api_base_url:
                        hahelper.set_sensor_measurements(sensor_type, f'sensor.{config.homeassistant.entity_prefix}_sensor_{sensor.name}_{sensor_type}', measurement)

            if sensor_type in measurements and measurements[sensor_type]:
                logging.debug(f'measurements[sensor_type].values(): {measurements[sensor_type].values()}')
                sensor_measurements_avg = statistics.mean(measurements[sensor_type].values())
                logging.debug(f'Aggregate {sensor_type} measurements: {sensor_measurements_avg}')
                measurements[sensor_type].update({'average': sensor_measurements_avg})

                if config.homeassistant.api_base_url:
                    hahelper.set_sensor_measurements(sensor_type, f'sensor.{config.homeassistant.entity_prefix}_pot_{self.pot_name}_{sensor_type}', measurements[sensor_type]['average'])

                if sensor_type == 'moisture':
                    self.moisture = sensor_measurements_avg
                    self.moisture_last_measurement = datetime.now()

        return measurements
