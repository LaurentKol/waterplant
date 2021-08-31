from datetime import datetime, timedelta
import statistics

from btlewrap.bluepy import BluepyBackend
from btlewrap.base import BluetoothBackendException

from miflora.miflora_poller import (MI_BATTERY, MI_CONDUCTIVITY, MI_LIGHT, MI_MOISTURE, MI_TEMPERATURE, MiFloraPoller)

class SensorsGroup:
    def __init__(self, sensors) -> None:
        self.sensor_pollers = {}
        self.last_battery_levels_checked = datetime.now() - timedelta(days=2)
        for sensor in sensors:
            self.sensor_pollers[sensor['name']] = MiFloraPoller(sensor['mac'], BluepyBackend)

    def get_moisture(self) -> int:
        moisture_measurements = []

        for sensor_name, sensor_poller in self.sensor_pollers.items():
            try:
                measurment = sensor_poller.parameter_value(MI_MOISTURE)
                print(f'{sensor_name} moisture measurement: {measurment}')
                moisture_measurements.append(measurment)
            except BluetoothBackendException:
                print(f'Failed to read from {sensor_name}')

        measurements_avg = statistics.mean(moisture_measurements)
        print(f'Aggregate moisture measurements: {measurements_avg}')

        return measurements_avg

    def check_battery(self) -> dict:
        battery_levels = {}
        for sensor_name, sensor_poller in self.sensor_pollers.items():
            try:
                measurment = sensor_poller.parameter_value(MI_BATTERY)
                print(f'{sensor_name} battery measurement: {measurment}')
                battery_levels[sensor_name] = measurment
                self.last_battery_levels_checked = datetime.now()
            except BluetoothBackendException:
                print(f'Failed to read from {sensor_name}')

        return battery_levels
