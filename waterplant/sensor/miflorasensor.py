from datetime import datetime, timedelta
import logging
from typing import List, Optional

from btlewrap.bluepy import BluepyBackend
from btlewrap.base import BluetoothBackendException
from miflora.miflora_poller import (MI_BATTERY, MI_CONDUCTIVITY, MI_LIGHT, MI_MOISTURE, MI_TEMPERATURE, MiFloraPoller)

from waterplant.config import config
from waterplant.homeassistant import hahelper
from .basesensor import BaseSensor

class MifloraSensor(BaseSensor):
    def __init__(self, **kwargs):
        super().__init__(kwargs['type'], kwargs['name'])
        self.mac = kwargs['mac']
        self.sensor_poller = MiFloraPoller(self.mac, BluepyBackend, cache_timeout=config.miflora_cache_timeout, adapter=config.miflora_bluetooth_adapter)

    def get_generic_measurement(self, mi_type) -> Optional[int]:
        try:
            measurement = self.sensor_poller.parameter_value(mi_type)
            # logging.debug(f'{self.name} {mi_type} measurement: {measurement}')
            self.last_successful_reading_ts = datetime.now()
            self.last_successful_reading_and_no_notification_ts = datetime.now()
            self.consecutive_failed_reading = 0
            return measurement
        except BluetoothBackendException as e:
            logging.warn(f'Failed to read {mi_type} from sensor {self.name}, {self.consecutive_failed_reading} consecutive failed readings, {self.last_successful_reading_ts} is last successful: {e}')
            self.consecutive_failed_reading += 1
            logging.debug(f'date condition:{self.last_successful_reading_and_no_notification_ts} and {datetime.now() - timedelta(days=3)}')
            if self.last_successful_reading_and_no_notification_ts < datetime.now() - timedelta(days=3):
                hahelper.send_push_notification(f'No readings from sensor {self.name} for 3 days, {self.consecutive_failed_reading} consecutive reading failures') 
                self.last_successful_reading_and_no_notification_ts = datetime.now()
                self.consecutive_failed_reading = 0
            return None

    def get_measurement(self, sensor_type: str) -> Optional[int]:
        mi_code_map = {'battery': MI_BATTERY, 'conductivity': MI_CONDUCTIVITY, 'light': MI_LIGHT, 'moisture': MI_MOISTURE, 'temperature': MI_TEMPERATURE}
        try:
            mi_code = mi_code_map[sensor_type]
            return self.get_generic_measurement(mi_code)
        except KeyError:
            logging.error(f'Unknown mi sensor code: {sensor_type}')
            return None
