from time import sleep
import threading

from waterplant.app import Waterplant
from waterplant.api.gqlapiserver import gql_api_server 
from waterplant.pot import Pot
from waterplant.config import config

#TODO: Use some proper logging instead of print()
if __name__ == '__main__':

    pots = []
    for pot in config.pots:
        # TODO: change to **kwargs
        pots.append(Pot(pot['name'], pot['dryness_threshold'], pot['max_watering_frequency_seconds'], pot['sprinkler_pump_pin'], pot['sensors']))

    waterplant_thread = threading.Thread(target=Waterplant.run, kwargs={'pots':pots})
    waterplant_thread.setDaemon(True)
    waterplant_thread.start()

    gql_api_server = gql_api_server.create_gql_api_server(pots=pots)
    gql_api_server_thread = threading.Thread(target=gql_api_server.run(host=config.api_listening_ip))
    gql_api_server_thread.setDaemon(True)
    gql_api_server_thread.start()
