import logging
from typing import List

from waterplant.config import config
from waterplant.pot import Pot
from waterplant.homeassistant import hahelper


def check_sensors(pots: List[Pot], sensor_types: List[str]):
    for pot in pots:
        for sensor_type in sensor_types:
            measurements = pot.sensors.get_measurements([sensor_type])
            logging.info(f'Pot: {pot.name}, sensor_type: {sensor_type}, measurements: {measurements}')
