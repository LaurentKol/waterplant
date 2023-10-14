import functools
import logging
from threading import Thread
from datetime import datetime, timedelta

from homeassistant_api import Client, HomeassistantAPIError
from requests.exceptions import RequestException

from waterplant.config import config

ha_client = None

if config.homeassistant.api_base_url and config.homeassistant.long_live_token:
    ha_integration_activated = True
else:
    ha_integration_activated = False

def connect() -> bool:
    global ha_client
    try:
        # TODO: Make timeout customizable from config, https://docs.python-requests.org/en/master/user/advanced/#timeouts , also sometime urllib3 timeout (300s) is not overriden
        ha_client = Client(api_url=config.homeassistant.api_base_url, token=config.homeassistant.long_live_token, global_request_kwargs={'timeout': (6.1, 27)})
        logging.info(f'Successfully connected to Home-assistant')
        return True
    except (RequestException, HomeassistantAPIError) as e:
        # TODO: Consider try client periodically if HA unreachable at start-up
        #       ATM state update is disabled if at start-up HA is unreachable, if failure happens after restart, retry does happen tho.
        logging.warn(f'Failed to connect to Home-assistant: {e}')
        ha_client = None
        return False

def is_connected() -> bool:
    if ha_client:
        return True
    else:
        return False

def ensure_connected() -> None:
    if ha_integration_activated and not is_connected():
        connect()

def set_state(kwargs) -> None:
    if is_connected():
        # state = State(**kwargs)
        # Thread(target=ha_client.set_state, kwargs={'state': state}).start()
        # TODO: This might raise homeassistant_api.errors.RequestError consider wrapping it try/except
        Thread(target=ha_client.set_state, kwargs=kwargs).start()

def set_moisture_level(entity_id, state) -> None:
    set_state({'entity_id': entity_id, 'state': state, 'attributes': {'device_class':'MOISTURE', 'state_class': 'measurement', 'unit_of_measurement': '%'}})

def set_sensor_measurements(sensor_type, entity_id, state) -> None:
    sensor_type_attributes_map = {'temperature': {'device_class':'TEMPERATURE', 'state_class': 'measurement', 'unit_of_measurement': '°C'},
                              'light': {'device_class':'ILLUMINANCE', 'state_class': 'measurement', 'unit_of_measurement': 'lx'},
                              'conductivity': {'device_class':'conductivity', 'state_class': 'measurement', 'unit_of_measurement': 'µS/cm'}, # Not a HA decice class
                              'moisture': {'device_class':'MOISTURE', 'state_class': 'measurement', 'unit_of_measurement': '%'},
                              'battery': {'device_class':'BATTERY', 'state_class': 'measurement', 'unit_of_measurement': '%'}}
    set_state({'entity_id': entity_id, 'state': state, 'attributes': sensor_type_attributes_map[sensor_type]})

def send_heartbeat() -> None:
    if ha_integration_activated and is_connected():
        set_state({'entity_id': f'sensor.{config.homeassistant.entity_prefix}_heartbeat', 'state': str(datetime.now()), 'attributes': {'device_class': 'timestamp', 'state_class': 'measurement' }})

def send_push_notification(message) -> None:
    if ha_integration_activated and is_connected() and config.homeassistant.notify_service:
        ha_client.trigger_service('notify', config.homeassistant.notify_service, title=f'Waterplant ({config.homeassistant.entity_prefix})', message=message)

def set_switch_on_off_state(func):
    #BUG: ha_client.set_state threads order is not guarantee.
    @functools.wraps(func)
    def wrapper_set_ha_state(*args, **kwargs):
        # Make sure that ha_client is configured and that "set_ha_state" is decorating a method of an instance with a "name" property'
        # if not, just called decorated method without update state in home-assitant. 
        if ha_client and args and len(args) > 0 and hasattr(args[0], 'name'):
            switch_name = f'{args[0].name}'
            entity_name = f'switch.{config.homeassistant.entity_prefix}_{switch_name}'
            # These threads terminated, at latest after timeout. Tested with "threading.enumerate()" and "iptables -A OUTPUT -p tcp --dport 8123 -j DROP"
            Thread(target=ha_client.set_state, kwargs={'entity_id':entity_name, 'state':'on', 'attributes':{'friendly_name':switch_name}}).start()
            value = func(*args, **kwargs)
            # TODO: join() on previous thread to ensure updates are sequential  
            Thread(target=ha_client.set_state, kwargs={'entity_id':entity_name, 'state':'off', 'attributes':{'friendly_name':switch_name}}).start()
        else:
            logging.debug(f'HA client is disabled, either in config or HA unreachable at start-up')
            value = func(*args, **kwargs)
        return value

    return wrapper_set_ha_state
