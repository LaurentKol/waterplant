import logging
from datetime import datetime

from waterplant.jobs.check_sensors import check_sensors
from waterplant.pot import Pot

'''Each of these "watering_triggers" functions might be called by check_watering jobs depending on config.py, this determine if pots gets watered'''

def dryness_threshold(pot: Pot, scheduler) -> bool:
    logging.debug(f'Checking dryness threshold for pot {pot.name}')

    if pot.sensors.moisture_last_measurement > pot.sprinkler.last_watering:
        if pot.sensors.moisture < pot.dryness_threshold:
            logging.info(f'Watering {pot.name} ({pot.sensors.moisture}% moist =< {pot.dryness_threshold}% moist threshold)')
            return True
        else:
            logging.info(f'{pot.name} is not dry enough ({pot.sensors.moisture}% moist > {pot.dryness_threshold}% moist threshold)')
            return False
    else:
        logging.warn(f'Last moisture measurement ({pot.sensors.moisture_last_measurement}) for {pot.name} is older than last watering ({pot.sprinkler.last_watering}), skipping watering trigger check and scheduling sensor check')
        scheduler.add_job(check_sensors, kwargs={'pots': [pot], 'sensor_types': ['moisture']}, id=f'check_sensors-{pot.name}', misfire_grace_time=600, run_date=datetime.now(), coalesce=True, executor='bluetooth')
        return False

def min_watering_time(pot: Pot, scheduler) -> bool:
    logging.debug(f'Checking minimum watering time for pot {pot.name}')
    if pot.sprinkler.last_watering + pot.min_watering_frequency < datetime.now():
        logging.info(f'Min watering time exceeded. Watering {pot.name}, regardless of ({pot.sensors.moisture}% =< {pot.dryness_threshold}% moisture threshold)')
        return True
    else:
        return False
