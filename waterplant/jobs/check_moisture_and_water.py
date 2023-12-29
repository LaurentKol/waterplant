import logging
from typing import List
from datetime import datetime, timedelta

from waterplant.pot import Pot
from waterplant.config import config
from waterplant.homeassistant import hahelper
from waterplant.jobs.water import water
from waterplant.jobs.check_sensors import check_sensors

def check_moisture_and_water(pots: List[Pot], scheduler):
    for pot in pots:
        if pot.sensors.moisture_last_measurement > pot.sprinkler.last_watering:
            logging.info(f'Last moisture measurement ({pot.sensors.moisture_last_measurement}) for {pot.name} is newer than last watering ({pot.sprinkler.last_watering})')
            if pot.sensors.moisture < pot.dryness_threshold:
                logging.info(f'Watering {pot.name} ({pot.sensors.moisture}% moist =< {pot.dryness_threshold}% moist threshold)')
                scheduler.add_job(water, kwargs={'pot': pot}, id=f'watering-{pot.name}', misfire_grace_time=600, coalesce=True, executor='watering')
                scheduler.add_job(check_sensors, kwargs={'pots': [pot], 'sensor_types': ['moisture']}, id=f'check_sensors-{pot.name}', misfire_grace_time=600, run_date=datetime.now() + timedelta(seconds = config.watering_duration_seconds + 10), coalesce=True, executor='bluetooth')
            else:
                logging.info(f'{pot.name} is not dry enough ({pot.sensors.moisture}% moist > {pot.dryness_threshold}% moist threshold)')
        else:
            logging.warn(f'Last moisture measurement ({pot.sensors.moisture_last_measurement}) for {pot.name} is older than last watering ({pot.sprinkler.last_watering}), skipping watering...')
            scheduler.add_job(check_sensors, kwargs={'pots': [pot], 'sensor_types': ['moisture']}, id=f'check_sensors-{pot.name}', misfire_grace_time=600, run_date=datetime.now(), coalesce=True, executor='bluetooth')
