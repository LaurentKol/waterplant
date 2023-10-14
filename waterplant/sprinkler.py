from datetime import datetime
from time import sleep
import logging

from RPi import GPIO

from waterplant.config import config
from waterplant.homeassistant import hahelper

class Sprinkler:
    def __init__(self, name: str, sprinkler_pin: int, sprinkler_pin_off_state: bool, disabled: bool) -> None:
        self.name = name
        self.sprinkler_pin = sprinkler_pin
        self.sprinkler_pin_off_state = sprinkler_pin_off_state
        self.last_watering = datetime.min
        self.is_watering_now = False
        self.disabled = disabled

    def __repr__(self) -> str:
        return f'{self.last_watering}'

    def enforce_off(self) -> None:
        if GPIO.input(self.sprinkler_pin) != self.sprinkler_pin_off_state:
            logging.warn(f'Sprinkler {self.name} was found turned on outside of water() method!!! Turning it off.')
            GPIO.output(self.sprinkler_pin, self.sprinkler_pin_off_state)

    @hahelper.set_switch_on_off_state
    def water(self, force: bool = False) -> None:
        if self.disabled and not force:
            logging.info(f'Sprinkler {self.name} is disabled, not watering')
            return

        drymode_msg = ' (dry-mode on, simulating)' if config.sprinkler_pump_drymode else ''

        logging.info(f'Turning on sprinkler {self.name} for {config.watering_duration_seconds}s{drymode_msg}')
        self.last_watering = datetime.now()

        self.is_watering_now = True
        if not config.sprinkler_pump_drymode:
            GPIO.output(self.sprinkler_pin, not self.sprinkler_pin_off_state)
        logging.info(f'Turned on sprinkler {self.name}{drymode_msg}')

        sleep(config.watering_duration_seconds)
        logging.debug(f'Sprinkler {self.name} is: {GPIO.input(self.sprinkler_pin)}')

        if not config.sprinkler_pump_drymode:
            GPIO.output(self.sprinkler_pin, self.sprinkler_pin_off_state)
        self.is_watering_now = False
        logging.info(f'Turned off sprinkler {self.name}{drymode_msg}')
