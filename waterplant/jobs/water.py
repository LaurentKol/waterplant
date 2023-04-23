import logging
from typing import List

from waterplant.pot import Pot

def water(pot: Pot, force: bool = False):
    logging.info(f'Watering {pot.name}')
    pot.sprinkler.water(force)
