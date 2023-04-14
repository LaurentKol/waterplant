import logging
from typing import List

from waterplant.pot import Pot

def water(pot: Pot):
    logging.info(f'Watering {pot.name}')
    pot.sprinkler.water()
