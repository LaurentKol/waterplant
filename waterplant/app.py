from datetime import time, datetime, timedelta
from time import sleep

from RPi import GPIO

from waterplant.config import config
from waterplant.pot import Pot

class Waterplant:

    # @staticmethod
    def run(pots):
        
        # Set pins' mode
        GPIO.setmode(GPIO.BOARD)

        # Set all pump off as we're not sure in which state pins are at start-up
        for pot in pots:
            GPIO.setup(pot.sprinkler_pump_pin, GPIO.OUT)
            GPIO.output(pot.sprinkler_pump_pin, True) # Set all off

        while True:
            # print(f'pots: {pots}')

            # Water now if force_next_watering was set (via API)
            for pot in pots:
                if pot.sprinkler.force_next_watering:
                    print(f'Force watering {pot.name}')
                    pot.sprinkler.water()
            
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
                        print(f'{pot.name} was watered recently ({last_watering_delta_seconds}s ago), skipping ...')
                        continue

                    # Skip if this pot is still moist
                    moisture_level = pot.sensors.get_moisture()
                    if moisture_level and moisture_level > pot.dryness_threshold:
                        print(f'{pot.name} is not dry enough ({moisture_level}% moist > {pot.dryness_threshold}% moist threshold)')
                        continue

                    print(f'Watering {pot.name}')
                    pot.sprinkler.water()
                # print(f'Sleeping {config.check_soil_freq_seconds}s ...')
                # sleep(config.check_soil_freq_seconds)

            print(f'Sleeping {config.check_for_watering_freq_seconds}s ...')
            sleep(config.check_for_watering_freq_seconds)
