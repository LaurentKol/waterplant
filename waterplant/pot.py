from .sensorgroup import SensorsGroup
from .sprinkler import Sprinkler

class Pot:
    def __init__(self, name, dryness_threshold, max_watering_frequency_seconds, sprinkler_pump_pin, sensors) -> None:
        self.name = name
        self.dryness_threshold = dryness_threshold
        self.max_watering_frequency_seconds = max_watering_frequency_seconds
        self.sprinkler_pump_pin = sprinkler_pump_pin
        self.sensors = SensorsGroup(sensors)
        self.sprinkler = Sprinkler(name, sprinkler_pump_pin)
