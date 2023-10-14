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
        if (moisture_levels := pot.sensors.get_moisture()):
            # TODO: Consider deduplicate this block from check_moisture
            hahelper.set_moisture_level(f'sensor.{config.homeassistant.entity_prefix}_{pot.name}_moisture', moisture_levels['average'])
            for sensor_name, measurement in moisture_levels.items():
                if not sensor_name == 'average':
                    hahelper.set_moisture_level(f'sensor.{config.homeassistant.entity_prefix}_{sensor_name}_moisture', measurement)

            if moisture_levels['average'] < pot.dryness_threshold:
                logging.info(f'Watering {pot.name} ({moisture_levels["average"]}% moist =< {pot.dryness_threshold}% moist threshold)')
                scheduler.add_job(water, kwargs={'pot': pot}, id=f'watering-{pot.name}', misfire_grace_time=600, coalesce=True, executor='watering')
                scheduler.add_job(check_sensors, kwargs={'pots': [pot], 'sensor_types': ['moisture']}, id=f'check_sensors-{pot.name}', misfire_grace_time=600, run_date=datetime.now() + timedelta(seconds = config.watering_duration_seconds + 10), coalesce=True, executor='bluetooth')
            else:
                logging.info(f'{pot.name} is not dry enough ({moisture_levels["average"]}% moist > {pot.dryness_threshold}% moist threshold)')
        else:
            logging.warn(f'Could not get moisture measurement for {pot.name}, skipping ...')