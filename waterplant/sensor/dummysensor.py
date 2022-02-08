import logging
from random import randint
from typing import Optional

from .basesensor import BaseSensor

class DummySensor(BaseSensor):
    def __init__(self, **kwargs):
        super().__init__(kwargs['type'], kwargs['name'])

    def get_moisture(self) -> Optional[int]:
        measurement = randint(0, 100)
        logging.debug(f'{self.name} moisture measurement: {measurement}')
        return measurement

    def get_battery(self) -> Optional[int]:
        return randint(0, 100)
