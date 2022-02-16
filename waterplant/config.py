from sys import exit
from datetime import time

import confuse
source = confuse.YamlSource('config.yaml')
unvalidated_config = confuse.RootView([source])
template = {
    'api_listening_ip': str,
    'check_for_watering_freq_seconds': 3,
    'check_battery_freq_days': 1,
    'logfile': '/tmp/waterplant.log',
    'loglevel': confuse.Choice(choices=['DEBUG','INFO','WARN','ERROR'], default='INFO'),
    'miflora_cache_timeout': 600, # That's default from miflora module: https://github.com/basnijholt/miflora/blob/be6161c6d56edfb95a1c6233a2ef9f5227040104/miflora/miflora_poller.py#L54
    'watering_schedule_time': {
        'from_hour': confuse.String(pattern='[0-9]{2}:[0-9]{2}'),
        'to_hour': confuse.String(pattern='[0-9]{2}:[0-9]{2}'),
    },
    'watering_duration_seconds': 30,
    'sprinkler_pump_drymode': bool,
    'homeassistant': {
        'api_base_url': confuse.Optional(confuse.String(default=None)),
        'long_live_token': confuse.Optional(confuse.String(default=None)),
    },
    'pots': confuse.Sequence({
        'name': str,
        'dryness_threshold': 30,
        'max_watering_freq': 300,
        'sprinkler_pin': 8,
        'sensors': confuse.Sequence({
            'type': confuse.Choice(choices=['Miflora','Dummy'], default='Miflora'), # TODO: Generate pattern from scanning existing waterplant.sensor.*
            'name': str,
            'mac': confuse.Optional(confuse.String(pattern='[0-9a-fA-F:]{17}')) # TODO: Make mac required if type is Miflora
        }),
    }),
}

try:
    config = unvalidated_config.get(template)
except confuse.exceptions.ConfigValueError as err:
    print(f'Config is invalid! Error is: {err}\nSee config.yaml.sample and make sure sensor.type is of an implement module/class.\nExiting ...')
    exit(1)
except confuse.ConfigError as err:
    print(err)
