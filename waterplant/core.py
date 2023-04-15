from typing import List

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from RPi import GPIO

from waterplant.config import config
from waterplant.pot import Pot
from waterplant.jobs.heartbeat import heartbeat
from waterplant.jobs.check_battery import check_battery
from waterplant.jobs.check_moisture import check_moisture
from waterplant.jobs.check_moisture_and_water import check_moisture_and_water
from waterplant.homeassistant import hahelper
from waterplant.homeassistant.hahelper import ensure_connected

class Waterplant:
    def __init__(self, pots: List[Pot]) -> None:
        self.pots = pots
        self.scheduler = BackgroundScheduler(executors= {
            'default': ThreadPoolExecutor(20),
            'watering': ThreadPoolExecutor(max_workers=1),
            'bluetooth': ThreadPoolExecutor(max_workers=1),
        })


    def start(self) -> None:
        # Set pins' mode
        GPIO.setmode(GPIO.BOARD)

        # Set all pump off as we're not sure in which state pins are at start-up
        for pot in self.pots:
            GPIO.setup(pot.sprinkler.sprinkler_pin, GPIO.OUT)
            GPIO.output(pot.sprinkler.sprinkler_pin, True) # Set all off

        hahelper.connect()
        self.scheduler.add_job(heartbeat, 'interval', seconds=config.homeassistant.heartbeat_freq_seconds)
        self.scheduler.add_job(ensure_connected, 'interval', 
                               seconds=config.homeassistant.connection_retry_freq_seconds)
        self.scheduler.add_job(check_battery, 'interval', hours=config.check_battery_freq_hours, misfire_grace_time=300, jitter=120, kwargs={'pots': self.pots}, coalesce=True, executor='bluetooth')
        self.scheduler.add_job(check_moisture, 'interval', minutes=config.check_moisture_freq_minutes, misfire_grace_time=300, jitter=120, kwargs={'pots': self.pots}, coalesce=True, executor='bluetooth')
        self.scheduler.add_job(check_moisture_and_water, 'cron', 
                               day=config.check_moisture_and_water_freq_cron.day, 
                               week=config.check_moisture_and_water_freq_cron.week, 
                               day_of_week=config.check_moisture_and_water_freq_cron.day_of_week, 
                               hour=config.check_moisture_and_water_freq_cron.hour, 
                               minute=config.check_moisture_and_water_freq_cron.minute, 
                               kwargs={'pots': self.pots, 'scheduler': self.scheduler}, coalesce=True, executor='bluetooth')

        self.scheduler.start()
