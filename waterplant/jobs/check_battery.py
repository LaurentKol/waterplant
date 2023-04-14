import logging
from typing import List

from waterplant.config import config
from waterplant.pot import Pot
from waterplant.homeassistant import hahelper

def check_battery(pots: List[Pot]):
    for pot in pots:
        battery_levels = pot.sensors.get_battery()
        for name, measurement in battery_levels.items():
            logging.debug(f'Sending to HA: sensor.{name}_battery {name}-battery {measurement}')
            hahelper.set_battery_level(f'sensor.waterplant_{name}_battery',measurement)
