import logging
from typing import List

from waterplant.pot import Pot
from waterplant.homeassistant import hahelper
from waterplant.jobs.water import water

def check_moisture_and_water(pots: List[Pot], scheduler):
    for pot in pots:
        if (moisture_levels := pot.sensors.get_moisture()):
            # TODO: Consider deduplicate this block from check_moisture
            hahelper.set_moisture_level(f'sensor.waterplant_{pot.name}_moisture', moisture_levels['average'])
            for sensor_name, measurement in moisture_levels.items():
                if not sensor_name == 'average':
                    hahelper.set_moisture_level(f'sensor.waterplant_{sensor_name}_moisture', measurement)

            if moisture_levels['average'] < pot.dryness_threshold:
                logging.info(f'Watering {pot.name} ({moisture_levels["average"]}% moist =< {pot.dryness_threshold}% moist threshold)')
                scheduler.add_job(water, kwargs={'pot': pot}, id=f'watering-{pot.name}', misfire_grace_time=600, coalesce=True, executor='watering')
            else:
                logging.info(f'{pot.name} is not dry enough ({moisture_levels["average"]}% moist > {pot.dryness_threshold}% moist threshold)')
        else:
            logging.warn(f'Could not get moisture measurement for {pot.name}, skipping ...')