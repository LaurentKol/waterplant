from collections import defaultdict
import logging
import requests
import statistics

from cachetools import cached, TTLCache

from waterplant.config import config


@cached(cache=TTLCache(maxsize=32, ttl=86400))  # Cache expires after 1 day
def get_historical_weather(start_date, end_date):
    base_url = "https://api.weatherapi.com/v1/history.json"
    params = {
        "key": config.weatherapi_com_key,
        "q": config.weatherapi_location,
        "dt": start_date,
        "end_dt": end_date
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from api.weatherapi.com: {e}")
        return None

    weather_data_raw = response.json()
    weather_data = defaultdict(list)

    location = weather_data_raw["location"]["name"]
    logging.info(f"Getting historical weather data from weatherapi.com (non-cached) ({start_date} to {end_date}, location: {location})")

    for forecast in weather_data_raw["forecast"]["forecastday"]:
        date = max_temp = forecast["date"]
        max_temp = forecast["day"]["maxtemp_c"]
        total_precip = forecast["day"]["totalprecip_mm"]
        weather_data['max_temp'].append(max_temp)
        weather_data['total_precip'].append(total_precip)
        logging.debug(f"Weather in {location} on {date}: {max_temp}°C, {total_precip}mm precipitation")

    weather_data_aggregates = {
        'avg_max_temp': statistics.mean(weather_data['max_temp']),
        'sum_precip': sum(weather_data['total_precip'])
    }

    logging.debug(f'weather_data_aggregates: {weather_data_aggregates}')

    return weather_data_aggregates
