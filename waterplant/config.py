from datetime import timedelta
import re
from sys import exit

import confuse


source = confuse.YamlSource('config.yaml')
unvalidated_config = confuse.RootView([source])
frequency_regexp = r'^(\d+)([d|h|m|s])$'

template = {
    'api_listening_ip': str,
    'check_sensors_freq_minutes': confuse.Integer(default=30),
    'sensor_types': confuse.StrSeq(default=['moisture']), #TODO: limit to (moisture|temperature|light|conductivity|battery)
    'watering_schedule_cron': { # Make sure this is less frequent then miflora_cache_timeout
        'day': confuse.Optional(confuse.String(default='*')),
        'week': confuse.Optional(confuse.String(default='*')),
        'day_of_week': confuse.Optional(confuse.String(default='*')),
        'hour': confuse.Optional(confuse.String(default='*')),
        'minute': confuse.Optional(confuse.String(default='0')),
    },
    'logfile': '/tmp/waterplant.log',
    'loglevel': confuse.Choice(choices=['DEBUG','INFO','WARN','ERROR'], default='INFO'),
    'miflora_bluetooth_adapter': confuse.Optional(confuse.String(default='hci0')),
    'miflora_cache_timeout': 600, # That's default from miflora module: https://github.com/basnijholt/miflora/blob/be6161c6d56edfb95a1c6233a2ef9f5227040104/miflora/miflora_poller.py#L54
    'watering_duration_seconds': 30,
    'sprinkler_pump_drymode': bool,
    'homeassistant': {
        'entity_prefix': confuse.Optional(confuse.String(default='waterplant')),
        'api_base_url': confuse.Optional(confuse.String(default=None)),
        'long_live_token': confuse.Optional(confuse.String(default=None)),
        'notify_service': confuse.Optional(confuse.String(default=None)),
        'connection_retry_freq_seconds': 1800,
        'heartbeat_freq_seconds': 60,
    },
    'pots': confuse.Sequence({
        'name': str,
        'watering_triggers': confuse.StrSeq(default=['dryness_threshold','min_watering_time']), #TODO: limit to (dryness_threshold|min_watering_time)
        'dryness_threshold': 30,
        # 'minimum_watering_days': confuse.Integer(default=None), # TODO: Implement this . Water at least every N days regardless of sensors value
        'min_watering_frequency': confuse.String(pattern=frequency_regexp, default='7d'),
        'max_watering_frequency': confuse.String(pattern=frequency_regexp, default='10m'),
        'sprinkler_pin': 8,
        'sprinkler_pin_off_state': confuse.Optional(bool, default=False), # False = GPIO.LOW and True = GPIO.HIGH
        'sprinkler_disabled': confuse.Optional(bool, default=False),
        'sensors': confuse.Sequence({
            'type': confuse.Choice(choices=['Miflora','Dummy'], default='Miflora'), # TODO: Generate pattern from scanning existing waterplant.sensor.*
            'name': str,
            'mac': confuse.Optional(confuse.String(pattern='[0-9a-fA-F:]{17}')) # TODO: Make mac required if type is Miflora
        }),
    }),
}

def parse_duration_string(input_str):
    '''Skipping validation here since it's already done in Confuse template'''
    match = re.match(frequency_regexp, input_str)
    if match:
        value, unit = map(match.group, [1, 2])
        unit_mapping = {'d': 'days', 'h': 'hours', 'm': 'minutes', 's': 'seconds'}

        duration = timedelta(**{unit_mapping[unit]: int(value)})
        return duration
    else:
        raise ValueError(f"Invalid input format. Use the pattern '{frequency_regexp}'.")

try:
    config = unvalidated_config.get(template)
except confuse.exceptions.ConfigValueError as err:
    print(f'Config is invalid! Error is: {err}\nSee config.yaml.sample and make sure sensor.type is of an implement module/class.\nExiting ...')
    exit(1)
except confuse.ConfigError as err:
    print(err)
