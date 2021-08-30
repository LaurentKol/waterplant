#!/usr/bin/python
from array import array
from numbers import Number
import statistics
import logging
from time import sleep
from datetime import time, datetime, timedelta

from btlewrap.bluepy import BluepyBackend
from btlewrap.base import BluetoothBackendException
from  RPi import GPIO
from miflora.miflora_poller import (
    MI_BATTERY,
    MI_CONDUCTIVITY,
    MI_LIGHT,
    MI_MOISTURE,
    MI_TEMPERATURE,
    MiFloraPoller,
)

LOGFILE='/var/log/water-plant.log'
LOGFILE='/tmp/water-plant.log'
logging.basicConfig(filename=LOGFILE,format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S', filemode='w', level=logging.DEBUG)

class SoilSensorsGroup:
    def __init__(self, sensors) -> None:
        self.sensor_pollers = {}
        self.last_battery_levels_checked = datetime.now() - timedelta(days=2)
        for sensor in sensors:
            self.sensor_pollers[sensor['name']] = MiFloraPoller(sensor['mac'], BluepyBackend)

    def get_moisture(self) -> int:
        moisture_measurements = []

        for sensor_name, sensor_poller in self.sensor_pollers.items():
            try:
                measurment = sensor_poller.parameter_value(MI_MOISTURE)
                print(f'{sensor_name} moisture measurement: {measurment}')
                moisture_measurements.append(measurment)
            except BluetoothBackendException:
                print(f'Failed to read from {sensor_name}')

        measurements_avg = statistics.mean(moisture_measurements)
        print(f'Aggregate moisture measurements: {measurements_avg}')

        return measurements_avg

    def check_battery(self) -> dict:
        battery_levels = {}
        for sensor_name, sensor_poller in self.sensor_pollers.items():
            try:
                measurment = sensor_poller.parameter_value(MI_BATTERY)
                print(f'{sensor_name} battery measurement: {measurment}')
                battery_levels[sensor_name] = measurment
                self.last_battery_levels_checked = datetime.now()
            except BluetoothBackendException:
                print(f'Failed to read from {sensor_name}')

        return battery_levels



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


class Pot:
    def __init__(self, name, dryness_threshold, max_watering_frequency_seconds, sprinkler_pump_pin, sensors) -> None:
        self.name = name
        self.dryness_threshold = dryness_threshold
        self.max_watering_frequency_seconds = max_watering_frequency_seconds
        self.sprinkler_pump_pin = sprinkler_pump_pin
        self.sensors = SoilSensorsGroup(sensors)
        self.sprinkler = Sprinkler(name, sprinkler_pump_pin)


CHECK_SOIL_FREQ_SECONDS = 10
CHECK_BATTERY_FREQ_DAYS = 1
WATERING_SCHEDULE_TIME = {'from': time(hour=0, minute=0),'to': time(hour=2, minute=0)}
WATERING_DURATION_SECONDS = 30
SPRINKLER_PUMP_DRYMODE=True

POTS = [
    Pot('balcony0', dryness_threshold=30, max_watering_frequency_seconds=30, sprinkler_pump_pin=8, 
        sensors=[{'name': 'balcony0a', 'mac': 'C4:7C:8D:63:C5:E8'}, {'name': 'balcony0b', 'mac': 'C4:7C:8D:63:EE:17'}]), # broken
    Pot('balcony1', dryness_threshold=30, max_watering_frequency_seconds=30, sprinkler_pump_pin=10, 
        sensors=[{'name': 'balcony1a', 'mac': 'C4:7C:8D:63:CB:49'}, {'name': 'balcony1b', 'mac': 'C4:7C:8D:63:EE:14'}]), # working
    Pot('balcony2', dryness_threshold=30, max_watering_frequency_seconds=30, sprinkler_pump_pin=16, 
        sensors=[{'name': 'balcony2a', 'mac': 'C4:7C:8D:67:64:39'}, {'name': 'balcony2b', 'mac': 'C4:7C:8D:63:EE:29'}]), # working
    Pot('balcony3', dryness_threshold=30, max_watering_frequency_seconds=30, sprinkler_pump_pin=18, 
        sensors=[{'name': 'balcony3a', 'mac': 'C4:7C:8D:67:63:EC'}, {'name': 'balcony3b', 'mac': 'C4:7C:8D:64:18:7A'}])
]


if not SPRINKLER_PUMP_DRYMODE:
    # Set pins' mode
    GPIO.setmode(GPIO.BOARD)

    # Set all pump off as we're not sure in which state pins are at start-up
    for pot in POTS:
        GPIO.setup(pot.sprinkler_pump_pin, GPIO.OUT)
        GPIO.output(pot.sprinkler_pump_pin, True) # Set all off

while True:
    # Only water plants during certain hours
    if (WATERING_SCHEDULE_TIME['from'] < datetime.now().time() < WATERING_SCHEDULE_TIME['to']):
        for pot in POTS:
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