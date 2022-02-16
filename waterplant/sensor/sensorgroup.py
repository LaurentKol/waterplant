import logging
import statistics
from typing import List, Optional
import importlib

from waterplant.config import config
from .basesensor import BaseSensor

class SensorsGroup:
    def __init__(self, name: str, sensors: List[BaseSensor]) -> None:
        self.name = name
        self.sensors = []
        for sensor in sensors:
            # Load the class named ${type}Sensor, if type is Miflora then MifloraSensor from miflorasensor.py
            SensorClass = getattr(importlib.import_module(f"waterplant.sensor.{sensor.type.lower()}sensor"), f'{sensor.type}Sensor')
            self.sensors.append(SensorClass(**sensor))

    def __repr__(self) -> str:
        return f'{self.sensors}'

    def get_moisture(self) -> Optional[int]:
        moisture_measurements = []

        for sensor in self.sensors:
            if (measurement := sensor.get_moisture()):
                moisture_measurements.append(measurement)

        if moisture_measurements:
            measurements_avg = statistics.mean(moisture_measurements)
            logging.debug(f'Aggregate moisture measurements: {measurements_avg}')
            return measurements_avg
        else:
            return None
