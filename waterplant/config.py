from datetime import time

import confuse
source = confuse.YamlSource('config.yaml')
unvalidated_config = confuse.RootView([source])
template = {
    'api_listening_ip': str,
    'check_for_watering_freq_seconds': 3,
    'check_battery_freq_days': 1,
    'miflora_cache_timeout': 600, # That's default from miflora module: https://github.com/basnijholt/miflora/blob/be6161c6d56edfb95a1c6233a2ef9f5227040104/miflora/miflora_poller.py#L54
    'watering_schedule_time': {
        'from_hour': confuse.String(pattern='[0-9]{2}:[0-9]{2}'),
        'to_hour': confuse.String(pattern='[0-9]{2}:[0-9]{2}'),
    },
    'watering_duration_seconds': 30,
    'sprinkler_pump_drymode': bool,
    'homeassistant': {
        'api_base_url': str,
        'long_live_token': str,
    },
    'pots': confuse.Sequence({
        'name': str,
        'dryness_threshold': 30,
        'max_watering_frequency_seconds': 300,
        'sprinkler_pump_pin': 8,
        'sensors': confuse.Sequence({
            'name': str,
            'mac': confuse.String(pattern='[0-9a-fA-F:]{17}')
        }),
    }),
}
config = unvalidated_config.get(template)