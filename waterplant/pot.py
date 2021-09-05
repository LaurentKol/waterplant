from .sensorgroup import SensorsGroup
from .sprinkler import Sprinkler

class Pot:
    '''Pot of plant contains a group of moisture sensors and a sprinkler'''
    #TODO: change to **kwargs
    def __init__(self, name, dryness_threshold, max_watering_frequency_seconds, sprinkler_pump_pin, sensors) -> None:
        self.name = name
        self.dryness_threshold = dryness_threshold
        self.max_watering_frequency_seconds = max_watering_frequency_seconds
        self.sensors = SensorsGroup(sensors)
        self.sprinkler = Sprinkler(name, sprinkler_pump_pin)

    def __repr__(self) -> str:
        return f'{self.name}: sensors:{self.sensors}, sprinkler:{self.sprinkler}'
