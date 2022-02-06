from datetime import time, datetime, timedelta
from time import sleep
import logging
from typing import List

from RPi import GPIO

from waterplant.config import config
from waterplant.pot import Pot

class Waterplant:

    # @staticmethod
    def run(pots: List[Pot]):
        
        # Set pins' mode
        GPIO.setmode(GPIO.BOARD)

        # Set all pump off as we're not sure in which state pins are at start-up
        for pot in pots:
            GPIO.setup(pot.sprinkler.sprinkler_pump_pin, GPIO.OUT)
            GPIO.output(pot.sprinkler.sprinkler_pump_pin, True) # Set all off

        while True:
            # Water now if force_next_watering was set (via API)
            for pot in pots:
                if pot.sprinkler.force_next_watering:
                    logging.info(f'Force watering {pot.name}')
                    pot.sprinkler.water()
                # Turn OFF Sprinkler if ON outside of water() method. This shouldn't be necessary
                pot.sprinkler.enforce_off()


            # TODO: Move this in a helper.py or make it more readable
            schedule_time_from = config.watering_schedule_time.from_hour.split(':')
            schedule_time_to = config.watering_schedule_time.to_hour.split(':')

            # If within watering schedule ...
            if (time(hour=int(schedule_time_from[0]), minute=int(schedule_time_from[1])) < datetime.now().time() < time(hour=int(schedule_time_to[0]), minute=int(schedule_time_to[1]))):
                for pot in pots:
                    # Check sensors' battery levels
                    if config.check_battery_freq_days != 0 and (datetime.now() - pot.sensors.last_battery_levels_checked).days > (config.check_battery_freq_days):
                        pot.sensors.check_battery()

                    # Skip this pot if watered recently
                    last_watering_delta_seconds = (datetime.now() - pot.sprinkler.last_watering).seconds
                    if  last_watering_delta_seconds < pot.max_watering_frequency_seconds:
                        logging.debug(f'{pot.name} was watered recently ({last_watering_delta_seconds}s ago), skipping ...')
                        continue

                    # Skip if this pot is still moist
                    moisture_level = pot.sensors.get_moisture()
                    if moisture_level and moisture_level > pot.dryness_threshold:
                        logging.debug(f'{pot.name} is not dry enough ({moisture_level}% moist > {pot.dryness_threshold}% moist threshold)')
                        continue
                    elif not moisture_level:
                        logging.warn(f'Could not get moisture measurement for {pot.name}, skipping ...')
                        continue

                    logging.info(f'Watering {pot.name} ({moisture_level}% moist =< {pot.dryness_threshold}% moist threshold)')
                    pot.sprinkler.water()

            logging.debug(f'Sleeping {config.check_for_watering_freq_seconds}s ...')
            sleep(config.check_for_watering_freq_seconds)
