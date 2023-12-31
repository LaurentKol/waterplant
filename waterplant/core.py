from typing import List
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from RPi import GPIO

from waterplant.config import config, parse_duration_string
from waterplant.pot import Pot
from waterplant.jobs.heartbeat import heartbeat
from waterplant.jobs.check_sensors import check_sensors
from waterplant.jobs.check_watering import check_watering
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
            GPIO.output(pot.sprinkler.sprinkler_pin, pot.sprinkler.sprinkler_pin_off_state) # Set all off

        hahelper.connect()
        self.scheduler.add_job(heartbeat, 'interval', next_run_time=datetime.now(), seconds=parse_duration_string(config.homeassistant.heartbeat_frequency).seconds)
        self.scheduler.add_job(ensure_connected, 'interval', 
                               seconds=parse_duration_string(config.homeassistant.connection_retry_frequency).seconds)
        self.scheduler.add_job(check_sensors, 'interval',
                               next_run_time=datetime.now() + timedelta(minutes=1), seconds=parse_duration_string(config.check_sensors_frequency).seconds, misfire_grace_time=30, coalesce=True, jitter=120,
                               kwargs={'pots': self.pots, 'sensor_types': config.sensor_types}, executor='bluetooth')
        self.scheduler.add_job(check_watering, 'cron', 
                               day=config.watering_schedule_cron.day, 
                               week=config.watering_schedule_cron.week, 
                               day_of_week=config.watering_schedule_cron.day_of_week, 
                               hour=config.watering_schedule_cron.hour, 
                               minute=config.watering_schedule_cron.minute, 
                               kwargs={'pots': self.pots, 'scheduler': self.scheduler}, misfire_grace_time=30, coalesce=True, executor='bluetooth')

        self.scheduler.start()
