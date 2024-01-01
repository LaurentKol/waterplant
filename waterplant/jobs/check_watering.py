import logging
from typing import List
from datetime import datetime, timedelta

from waterplant.pot import Pot
from waterplant.config import config
from waterplant.jobs.water import water
from waterplant.jobs.check_sensors import check_sensors
from waterplant import watering_trigger


def check_watering(pots: List[Pot], scheduler):
    '''Test each watering_triggers for each pots (as defined in config) and schedule job to water pots accordingly'''
    for pot in pots:
        if pot.sprinkler.last_watering + pot.max_watering_frequency > datetime.now():
            logging.info(f'Pot {pot.name} was recently watered ({pot.sprinkler.last_watering} + {pot.max_watering_frequency} > now), skipping watering trigger checks')
            continue

        for watering_trigger_check_func_name in pot.watering_triggers:
            watering_trigger_check_func = getattr(watering_trigger, watering_trigger_check_func_name)
            if watering_trigger_check_func(pot, scheduler):
                scheduler.add_job(water, kwargs={'pot': pot}, id=f'watering-{pot.name}', misfire_grace_time=600, coalesce=True, executor='watering')
                scheduler.add_job(check_sensors, kwargs={'pots': [pot], 'sensor_types': ['moisture']}, id=f'check_sensors-{pot.name}', misfire_grace_time=600, run_date=datetime.now() + timedelta(seconds = config.watering_duration_seconds + 10), coalesce=True, executor='bluetooth')
