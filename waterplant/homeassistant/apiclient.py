import functools
import logging

from homeassistant_api import Client

from waterplant.config import config

if config.homeassistant.api_base_url and config.homeassistant.long_live_token:
    # TODO: Use AsyncClient
    ha_client = Client(config.homeassistant.api_base_url, config.homeassistant.long_live_token)
else:
    ha_client = None

def set_ha_state(func):
    @functools.wraps(func)
    def wrapper_set_ha_state(*args, **kwargs):
        if args and len(args) > 0 and hasattr(args[0], 'name') and ha_client:
            switch_name = f'waterplant_{args[0].name}'
            entity_name = f'switch.{switch_name}'

            logging.debug(f'Set HA state "on" for {entity_name}')
            ha_client.set_state(entity_id=entity_name, state='on', attributes={'friendly_name':switch_name})

            value = func(*args, **kwargs)

            logging.debug(f'Set HA state "off" for {entity_name}')
            ha_client.set_state(entity_id=entity_name, state='off', attributes={'friendly_name':switch_name})
        else:
            value = func(*args, **kwargs)
        return value
    return wrapper_set_ha_state
