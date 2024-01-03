import logging
from datetime import datetime, timedelta

import numpy as np

from waterplant.jobs.check_sensors import check_sensors
from waterplant.pot import Pot
from waterplant.config import config
from waterplant.api.weatherapiclient import get_historical_weather

'''Each of these "watering_triggers" functions might be called by check_watering jobs depending on config.py, this determine if pots gets watered'''

def dryness_threshold(pot: Pot, scheduler) -> bool:
    if pot.sensors.moisture_last_measurement > pot.sprinkler.last_watering:
        if pot.sensors.moisture < pot.dryness_threshold:
            logging.info(f'Pot {pot.name} - Dryness check: Watering ({pot.sensors.moisture}% moist =< {pot.dryness_threshold}% moist threshold)')
            return True
        else:
            logging.info(f'Pot {pot.name} - Dryness check: Pot is not dry enough ({pot.sensors.moisture}% moist > {pot.dryness_threshold}% moist threshold)')
            return False
    else:
        logging.warn(f'Pot {pot.name} - Dryness check: Last moisture measurement ({pot.sensors.moisture_last_measurement}) for {pot.name} is older than last watering ({pot.sprinkler.last_watering}), skipping watering trigger check and scheduling sensor check')
        scheduler.add_job(check_sensors, kwargs={'pots': [pot], 'sensor_types': ['moisture']}, id=f'check_sensors-{pot.name}', misfire_grace_time=600, run_date=datetime.now(), coalesce=True, executor='bluetooth')
        return False

def min_watering_time_basic(pot: Pot, scheduler) -> bool:
    if pot.sprinkler.last_watering + pot.min_watering_frequency < datetime.now():
        logging.info(f'Pot {pot.name} - Min watering time check: Time exceeded. Watering')
        return True
    else:
        logging.info(f'Pot {pot.name} - Min watering time check: Time not exceeded ({pot.sprinkler.last_watering} + {pot.min_watering_frequency} > now)')
        return False

def min_watering_time_recent_weather(pot: Pot, scheduler) -> bool:
    '''Interpolate minimum watering time based on recent weather conditions and config, and compare against sprinkler's last watering date/time'''
    def get_date_range_from_config():
        now_dt = datetime.now()
        date_n_days_ago_dt = now_dt - timedelta(days=config.weatherapi_range_days)

        date_now = now_dt.strftime('%Y-%m-%d')
        date_n_days_ago = date_n_days_ago_dt.strftime('%Y-%m-%d')
        return date_n_days_ago, date_now

    def get_interpollated_min_watering_days(weather_data):
        # Map config list of tuple into 2 list for interpolation
        avg_max_temp, min_water_day = list(map(list, zip(*pot.min_watering_time_recent_weather)))

        min_watering_days = np.interp(weather_data['avg_max_temp'], np.array(avg_max_temp), np.array(min_water_day))
        return min_watering_days

    date_n_days_ago, date_now = get_date_range_from_config()
    weather_data = get_historical_weather(date_n_days_ago, date_now)
    min_watering_days = get_interpollated_min_watering_days(weather_data)

    if pot.sprinkler.last_watering + timedelta(days=min_watering_days) < datetime.now():
        logging.info(f'Pot {pot.name} - Min watering time by recent weather check: Time exceeded ({pot.sprinkler.last_watering} + {min_watering_days} days < now). Watering')
        return True
    else:
        logging.info(f'Pot {pot.name} - Min watering time by recent weather check: Time not exceeded ({pot.sprinkler.last_watering} + {min_watering_days} days > now)')
        return False
