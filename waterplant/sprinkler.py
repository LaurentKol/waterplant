from datetime import datetime
from time import sleep

from RPi import GPIO

from .config import WATERING_DURATION_SECONDS, SPRINKLER_PUMP_DRYMODE

class Sprinkler:
    def __init__(self, name, sprinkler_pump_pin) -> None:
        self.name = name
        self.sprinkler_pump_pin = sprinkler_pump_pin
        self.last_watering = datetime.now()

    def water(self) -> None:
        print(f'Turning on sprinkler pump {self.name} for {WATERING_DURATION_SECONDS}s')
        self.last_watering = datetime.now()
        if SPRINKLER_PUMP_DRYMODE:
            print(f'Running in sprinlker dry mode')
            return
        GPIO.output(self.sprinkler_pump_pin, False)
        sleep(WATERING_DURATION_SECONDS)
        GPIO.output(self.sprinkler_pump_pin, True)
