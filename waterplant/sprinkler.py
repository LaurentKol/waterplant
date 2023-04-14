from datetime import datetime, timedelta
from time import sleep
import logging

from RPi import GPIO

from waterplant.config import config
from waterplant.homeassistant import hahelper

class Sprinkler:
    def __init__(self, name: str, sprinkler_pin: int) -> None:
        self.name = name
        self.sprinkler_pin = sprinkler_pin
        self.last_watering = datetime.now() - timedelta(minutes=5) # TODO: Instead of 5min default, use max_watering_freq from pot's config.

    def __repr__(self) -> str:
        return f'{self.last_watering}'

    def enforce_off(self) -> None:
        if GPIO.input(self.sprinkler_pin) != 1:
            logging.warn(f'Sprinkler {self.name} was found turned on outside of water() method!!! Turning it off.')
            GPIO.output(self.sprinkler_pin, True)

    @hahelper.set_switch_on_off_state
    def water(self) -> None:
        drymode_msg = ' (dry-mode on, simulating)' if config.sprinkler_pump_drymode else ''

        logging.info(f'Turning on sprinkler {self.name} for {config.watering_duration_seconds}s{drymode_msg}')
        self.last_watering = datetime.now()

        if not config.sprinkler_pump_drymode:
            GPIO.output(self.sprinkler_pin, False)
        logging.info(f'Turned on sprinkler {self.name}{drymode_msg}')

        sleep(config.watering_duration_seconds)
        logging.debug(f'Sprinkler {self.name} is: {GPIO.input(self.sprinkler_pin)}')

        if not config.sprinkler_pump_drymode:
            GPIO.output(self.sprinkler_pin, True)
        logging.info(f'Turned off sprinkler {self.name}{drymode_msg}')
