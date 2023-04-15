from datetime import datetime, timedelta
import logging
from typing import List, Optional

from btlewrap.bluepy import BluepyBackend
from btlewrap.base import BluetoothBackendException
from miflora.miflora_poller import (MI_BATTERY, MI_CONDUCTIVITY, MI_LIGHT, MI_MOISTURE, MI_TEMPERATURE, MiFloraPoller)

from waterplant.config import config
from .basesensor import BaseSensor

class MifloraSensor(BaseSensor):
    def __init__(self, **kwargs):
        super().__init__(kwargs['type'], kwargs['name'])
        self.mac = kwargs['mac']
        self.sensor_poller = MiFloraPoller(self.mac, BluepyBackend, cache_timeout=config.miflora_cache_timeout)

    def get_generic_measurement(self, mi_type) -> Optional[int]:
        try:
            measurement = self.sensor_poller.parameter_value(mi_type)
            logging.debug(f'{self.name} {mi_type} measurement: {measurement}')
            return measurement
        except BluetoothBackendException as e:
            logging.warn(f'Failed to read {mi_type} from sensor {self.name}: {e}')
            return None

    def get_moisture(self) -> Optional[int]:
        return self.get_generic_measurement(MI_MOISTURE)

    def get_measurement(self, sensor_type: str) -> Optional[int]:
        mi_code_map = {'battery': MI_BATTERY, 'conductivity': MI_CONDUCTIVITY, 'light': MI_LIGHT, 'moisture': MI_MOISTURE, 'temperature': MI_TEMPERATURE}
        try:
            mi_code = mi_code_map[sensor_type]
            return self.get_generic_measurement(mi_code)
        except KeyError:
            logging.error(f'Unknown mi sensor code: {sensor_type}')
            return None

    def get_battery(self) -> Optional[int]:
        return self.get_generic_measurement(MI_BATTERY)
