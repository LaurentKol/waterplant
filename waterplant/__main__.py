from time import sleep
import threading
import logging
import signal
import sys

from RPi import GPIO

from waterplant.core import Waterplant
from waterplant.api.gqlapiserver import GqlApiServer 
from waterplant.pot import Pot
from waterplant.config import config

if __name__ == '__main__':

    logging.basicConfig(
        filename=config.logfile,format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S %Z',
        level=logging.getLevelName(config.loglevel),
        force=True
    )
    logging.info('Waterplant app starting')
    logging.debug(f'Config is {config}')

    pots = []
    for pot in config.pots:
        # See config.py for list of possible attributes of pot. 
        pots.append(Pot(**pot))

    waterplant = Waterplant(pots)
    waterplant.start()
    logging.debug('Waterplant app started')

    # Wrapping API Server in a method because target needs a callable, if not wrapped it's not called 
    def gql_api_server():
        GqlApiServer.create_gql_api_server(pots=pots, scheduler=waterplant.scheduler).run(host=config.api_listening_ip)
    
    logging.debug('GraphQL API server starting')
    threading.Thread(target=gql_api_server, daemon=True).start()

    # Cleanup GPIOs when exiting
    def signal_handler(sig, frame):
        print('You pressed Ctrl+C! Cleaning-up GPIOs ...')
        GPIO.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C to exit')
    signal.pause()