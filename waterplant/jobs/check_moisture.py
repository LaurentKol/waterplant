import logging
from typing import List

from waterplant.pot import Pot
from waterplant.homeassistant import hahelper


def check_moisture(pots: List[Pot]):
    for pot in pots:
        if (moisture_levels := pot.sensors.get_moisture()):
            hahelper.set_moisture_level(f'sensor.waterplant_{pot.name}_moisture', moisture_levels['average'])
            for sensor_name, measurement in moisture_levels.items():
                if not sensor_name == 'average':
                    hahelper.set_moisture_level(f'sensor.waterplant_{sensor_name}_moisture', measurement)
        else:
            logging.warn(f'Could not get moisture measurement for {pot.name}, skipping ...')
