from typing import List, Dict

from .sensor.sensorgroup import SensorsGroup
from .sprinkler import Sprinkler
from .config import parse_duration_string

class Pot:
    '''Pot of plant contains a group of moisture sensors and a sprinkler'''
    def __init__(self,
                 name: str,
                 watering_triggers: List[str],
                 dryness_threshold: int,
                 min_watering_frequency: str,
                 max_watering_frequency: str,
                 sprinkler_pin: int,
                 sprinkler_pin_off_state: bool,
                 sprinkler_disabled: bool,
                 sensors: List[Dict]
                 ) -> None:
        self.name = name
        self.watering_triggers = watering_triggers
        self.dryness_threshold = dryness_threshold
        self.min_watering_frequency = parse_duration_string(min_watering_frequency)
        self.max_watering_frequency = parse_duration_string(max_watering_frequency)
        self.sensors = SensorsGroup(name, sensors)
        self.sprinkler = Sprinkler(name, sprinkler_pin, sprinkler_pin_off_state, sprinkler_disabled)

    def __repr__(self) -> str:
        return f'{self.name}: sensors:{self.sensors}, sprinkler:{self.sprinkler}'
