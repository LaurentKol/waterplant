import logging
from typing import List

from waterplant.pot import Pot
from waterplant.homeassistant.hahelper import send_push_notification

def water(pot: Pot, force: bool = False):
    send_push_notification(f'Watering {pot.name} now')
    logging.info(f'Watering {pot.name}')
    pot.sprinkler.water(force)
