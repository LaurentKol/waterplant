from datetime import datetime
from time import sleep
import logging

from RPi import GPIO

from waterplant.config import config

class Sprinkler:
    def __init__(self, name: str, sprinkler_pump_pin: int) -> None:
        self.name = name
        self.sprinkler_pump_pin = sprinkler_pump_pin
        self.last_watering = datetime.now()
        self.force_next_watering = False

    def __repr__(self) -> str:
        return f'{self.last_watering}'

    def enforce_off(self) -> None:
        if GPIO.input(self.sprinkler_pump_pin) != 1:
            logging.warn(f'Sprinkler {self.name} was found turned on outside of water() method!!! Turning it off.')
            GPIO.output(self.sprinkler_pump_pin, True)

    def set_force_next_watering(self, force: bool) -> None:
        self.force_next_watering = force

    def water(self) -> None:
        drymode_msg = '(dry-mode on, simulating)' if config.sprinkler_pump_drymode else ''
        logging.info(f'Turning on sprinkler {self.name} for {config.watering_duration_seconds}s {drymode_msg}')
        self.last_watering = datetime.now()
        self.set_force_next_watering(False)
        if not config.sprinkler_pump_drymode:
            GPIO.output(self.sprinkler_pump_pin, False)
            logging.info(f'Turned on sprinkler {self.name}')
            sleep(config.watering_duration_seconds)
            logging.debug(f'Sprinkler {self.name} is: {GPIO.input(self.sprinkler_pump_pin)}')
            GPIO.output(self.sprinkler_pump_pin, True)
            logging.info(f'Turned off sprinkler {self.name}')
