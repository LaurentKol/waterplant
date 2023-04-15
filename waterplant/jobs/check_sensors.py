import logging
from typing import List

from waterplant.pot import Pot
from waterplant.homeassistant import hahelper


def check_sensors(pots: List[Pot], sensor_types: List[str]):
    for sensor_type in sensor_types:
        for pot in pots:
            measurements = pot.sensors.get_measurements([sensor_type])
            if measurements and sensor_type in measurements and 'average' in measurements[sensor_type]:
                hahelper.set_sensor_measurements(sensor_type, f'sensor.waterplant_{pot.name}_{sensor_type}', measurements[sensor_type]['average'])
                for sensor_name, measurement in measurements[sensor_type].items():
                    if not sensor_name == 'average':
                        hahelper.set_sensor_measurements(sensor_type, f'sensor.waterplant_{sensor_name}_{sensor_type}', measurement)
            else:
                logging.warn(f'Could not get moisture measurement for {sensor_type} for {pot.name}, skipping ...')
