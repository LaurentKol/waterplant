import functools
import logging
from threading import Thread
from datetime import datetime, timedelta

from homeassistant_api import Client, HomeassistantAPIError
from requests.exceptions import RequestException

from waterplant.config import config

ha_client = None
last_connect_retry = datetime.now() - timedelta(seconds=config.homeassistant.connection_retry_freq)

def connect() -> bool:
    global ha_client
    try:
        # TODO: Make timeout customizable from config, https://docs.python-requests.org/en/master/user/advanced/#timeouts , also sometime urllib3 timeout (300s) is not overriden
        ha_client = Client(api_url=config.homeassistant.api_base_url, token=config.homeassistant.long_live_token, global_request_kwargs={'timeout': (6.1, 27)})
        logging.info(f'Connect successfully to Home-assistant')
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
    global last_connect_retry
    now = datetime.now()
    if config.homeassistant.api_base_url and config.homeassistant.long_live_token \
        and not is_connected() and (now - last_connect_retry).total_seconds() > config.homeassistant.connection_retry_freq:
        last_connect_retry = datetime.now()
        connect()

def set_switch_on_off_state(func):
    @functools.wraps(func)
    def wrapper_set_ha_state(*args, **kwargs):
        # Make sure that ha_client is configured and that "set_ha_state" is decorating a method of an instance with a "name" property'
        # if not, just called decorated method without update state in home-assitant. 
        if ha_client and args and len(args) > 0 and hasattr(args[0], 'name'):
            switch_name = f'waterplant_{args[0].name}'
            entity_name = f'switch.{switch_name}'
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
