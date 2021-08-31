from datetime import time, datetime, timedelta
from time import sleep

from RPi import GPIO

from .config import CHECK_BATTERY_FREQ_DAYS, CHECK_SOIL_FREQ_SECONDS, CHECK_BATTERY_FREQ_DAYS, WATERING_SCHEDULE_TIME, WATERING_DURATION_SECONDS, SPRINKLER_PUMP_DRYMODE, POTS
from .pot import Pot

class Waterplant:

    @staticmethod
    def run():
        pots = []
        for pot in POTS:
            pots.append(Pot(pot['name'], pot['dryness_threshold'], pot['max_watering_frequency_seconds'], pot['sprinkler_pump_pin'], pot['sensors']))

        
        # Set pins' mode
        GPIO.setmode(GPIO.BOARD)

        # Set all pump off as we're not sure in which state pins are at start-up
        for pot in pots:
            GPIO.setup(pot.sprinkler_pump_pin, GPIO.OUT)
            GPIO.output(pot.sprinkler_pump_pin, True) # Set all off

        while True:
            # Only water plants during certain hours
            if (WATERING_SCHEDULE_TIME['from'] < datetime.now().time() < WATERING_SCHEDULE_TIME['to']):
                for pot in pots:
                    # Check sensors' battery levels
                    if (datetime.now() - pot.sensors.last_battery_levels_checked).days > (CHECK_BATTERY_FREQ_DAYS):
                        pot.sensors.check_battery()

                    # Skip if this pot was watered recently
                    last_watering_delta_seconds = (datetime.now() - pot.sprinkler.last_watering).seconds
                    if  last_watering_delta_seconds < pot.max_watering_frequency_seconds:
                        print(f'{pot.name} was watered recently ({last_watering_delta_seconds}s ago), skipping ...')
                        continue

                    # Skip if this pot is still moist
                    moisture_level = pot.sensors.get_moisture()
                    if moisture_level and moisture_level > pot.dryness_threshold:
                        print(f'{pot.name} is not dry enough')
                        continue

                    print(f'Watering {pot.name}')
                    pot.sprinkler.water()

            print(f'Sleeping {CHECK_SOIL_FREQ_SECONDS}s ...')
            sleep(CHECK_SOIL_FREQ_SECONDS)
