from typing import List

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from RPi import GPIO

from waterplant.config import config
from waterplant.pot import Pot
from waterplant.jobs.heartbeat import heartbeat
from waterplant.jobs.battery_check import battery_check
from waterplant.jobs.moisture_check import moisture_check
from waterplant.jobs.watering_moisture_check import watering_moisture_check
from waterplant.homeassistant import hahelper
from waterplant.homeassistant.hahelper import ensure_connected

class Waterplant:
    def __init__(self, pots: List[Pot]) -> None:
        self.pots = pots
        self.scheduler = BackgroundScheduler(executors= {
            'default': ThreadPoolExecutor(20),
            'watering': ThreadPoolExecutor(max_workers=1),
            'bluetooth': ThreadPoolExecutor(max_workers=1),
            'ha_executor': ThreadPoolExecutor(max_workers=5)
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
        self.scheduler.add_job(ensure_connected, 'interval', seconds=config.homeassistant.connection_retry_freq_seconds)
        self.scheduler.add_job(battery_check, 'interval', kwargs={'pots': self.pots}, misfire_grace_time=300, hours=config.check_battery_freq_hours, jitter=120, coalesce=True, executor='bluetooth')
        self.scheduler.add_job(moisture_check, 'interval', kwargs={'pots': self.pots}, misfire_grace_time=300, minutes=5, jitter=120, coalesce=True, executor='bluetooth')
        self.scheduler.add_job(watering_moisture_check, 'cron', day=config.watering_schedule_cron.day, week=config.watering_schedule_cron.week, day_of_week=config.watering_schedule_cron.day_of_week, hour=config.watering_schedule_cron.hour, minute=config.watering_schedule_cron.minute, kwargs={'pots': self.pots, 'scheduler': self.scheduler}, coalesce=True, executor='bluetooth')

        self.scheduler.start()
