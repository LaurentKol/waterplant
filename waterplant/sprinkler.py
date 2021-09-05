from datetime import datetime
from time import sleep

from RPi import GPIO

from waterplant.config import config

class Sprinkler:
    def __init__(self, name, sprinkler_pump_pin) -> None:
        self.name = name
        self.sprinkler_pump_pin = sprinkler_pump_pin
        self.last_watering = datetime.now()
        self.force_next_watering = False

    def __repr__(self) -> str:
        return f'{self.last_watering}'

    def set_force_next_watering(self, force) -> None:
        self.force_next_watering = force

    def water(self) -> None:
        print(f'Turning on sprinkler pump {self.name} for {config.watering_duration_seconds}s')
        self.last_watering = datetime.now()
        self.set_force_next_watering(False)
        if config.sprinkler_pump_drymode:
            print(f'Running in sprinlker dry mode')
        else:
            GPIO.output(self.sprinkler_pump_pin, False)
            sleep(config.watering_duration_seconds)
            GPIO.output(self.sprinkler_pump_pin, True)
