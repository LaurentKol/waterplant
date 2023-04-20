from typing import List, Dict

from .sensor.sensorgroup import SensorsGroup
from .sprinkler import Sprinkler

class Pot:
    '''Pot of plant contains a group of moisture sensors and a sprinkler'''
    def __init__(self, name: str, dryness_threshold: int, sprinkler_pin: int, sprinkler_disabled: bool, sensors: List[Dict]) -> None:
        self.name = name
        self.dryness_threshold = dryness_threshold
        self.sensors = SensorsGroup(name, sensors)
        self.sprinkler = Sprinkler(name, sprinkler_pin, sprinkler_disabled)

    def __repr__(self) -> str:
        return f'{self.name}: sensors:{self.sensors}, sprinkler:{self.sprinkler}'
