from datetime import time

CHECK_SOIL_FREQ_SECONDS = 15
CHECK_BATTERY_FREQ_DAYS = 1
WATERING_SCHEDULE_TIME = {'from': time(hour=00, minute=00),'to': time(hour=23, minute=59)}
WATERING_DURATION_SECONDS = 30
SPRINKLER_PUMP_DRYMODE = False

POTS = [
    {'name': 'balcony0', 'dryness_threshold': 30, 'max_watering_frequency_seconds': 300, 'sprinkler_pump_pin': 8, 'sensors': [{'name': 'balcony0a', 'mac': 'C4:7C:8D:63:C5:E8'}, {'name': 'balcony0b', 'mac': 'C4:7C:8D:63:EE:17'}]},
    {'name': 'balcony1', 'dryness_threshold': 30, 'max_watering_frequency_seconds': 300, 'sprinkler_pump_pin': 10, 'sensors': [{'name': 'balcony1a', 'mac': 'C4:7C:8D:63:CB:49'}, {'name': 'balcony1b', 'mac': 'C4:7C:8D:63:EE:14'}]},
    {'name': 'balcony2', 'dryness_threshold': 30, 'max_watering_frequency_seconds': 300, 'sprinkler_pump_pin': 16, 'sensors': [{'name': 'balcony2a', 'mac': 'C4:7C:8D:67:64:39'}, {'name': 'balcony2b', 'mac': 'C4:7C:8D:63:EE:29'}]},
    {'name': 'balcony3', 'dryness_threshold': 30, 'max_watering_frequency_seconds': 300, 'sprinkler_pump_pin': 18, 'sensors': [{'name': 'balcony3a', 'mac': 'C4:7C:8D:67:63:EC'}, {'name': 'balcony3b', 'mac': 'C4:7C:8D:64:18:7A'}]},
]
