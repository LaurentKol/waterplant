import logging

from waterplant.homeassistant import hahelper

def heartbeat():
    logging.debug('Sending heartbeat')
    hahelper.send_heartbeat()
