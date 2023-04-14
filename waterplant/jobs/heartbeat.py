import logging

from waterplant.homeassistant import hahelper

def heartbeat():
    hahelper.send_heartbeat()
    logging.debug('Sending heartbeat')