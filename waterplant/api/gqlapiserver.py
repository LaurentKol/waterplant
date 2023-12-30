from datetime import datetime
import logging
from typing import List, TypeVar

import strawberry
from flask import Flask
from strawberry.flask.views import GraphQLView
from apscheduler.schedulers.base import BaseScheduler

from waterplant.pot import Pot
from waterplant.jobs.water import water
from waterplant.config import config

class GqlApiServer:
    def create_gql_api_server(pots: List[Pot], scheduler: BaseScheduler) -> Flask:

        def get_sprinkler_watering_now(root: "Pot") -> bool:
            return root.sprinkler.is_watering_now

        def get_sprinkler_last_watering(root: "Pot") -> datetime:
            return root.sprinkler.last_watering

        @strawberry.type
        class Pot:
            name: str
            dryness_threshold: int
            sprinkler_last_watering: datetime = strawberry.field(resolver=get_sprinkler_last_watering)
            sprinkler_watering_now: bool = strawberry.field(resolver=get_sprinkler_watering_now)

        @strawberry.type
        class checkMoistureAndWaterFreqCronConfig:
            day: str
            week: str
            day_of_week: str
            hour: str
            minute: str

        @strawberry.type
        class homeassistantConfig:
            api_base_url: str
            connection_retry_freq_seconds: int
            heartbeat_freq_seconds: int

        @strawberry.type
        class SensorConfig:
            type: str
            name: str
            mac: str

        @strawberry.type
        class PotConfig:
            name: str
            dryness_threshold: int
            sprinkler_pin: int
            sprinkler_pin_off_state: bool
            sprinkler_disabled: bool
            sensors: List[SensorConfig]

        @strawberry.type
        class Config:
            api_listening_ip: str
            check_sensors_freq_minutes: int
            sensor_types: List[str]
            watering_schedule_cron: checkMoistureAndWaterFreqCronConfig
            logfile: str
            loglevel: str
            miflora_cache_timeout: int
            watering_duration_seconds: int
            sprinkler_pump_drymode: bool
            homeassistant: homeassistantConfig
            pots: List[PotConfig]

        @strawberry.type
        class Query:
            @strawberry.field
            def pots(self) -> List[Pot]:
                return pots

            @strawberry.field
            def pot(self, info: strawberry.types.Info, name: str) -> Pot:
                pot = [pot for pot in pots if pot.name == name].pop()
                return pot

            @strawberry.field
            def config(self) -> Config:
                return config


        @strawberry.type
        class Mutation:
            @strawberry.mutation
            def sprinkler_force_watering(self, name: str) -> str:
                if(pot := next((p for p in pots if p.name == name), None)):
                    logging.info(f'[GQL] Got force watering {name}, scheduling watering job')
                    scheduler.add_job(water, kwargs={'pot': pot, 'force': True}, id=f'watering-{pot.name}', misfire_grace_time=60, coalesce=True, executor='watering')
                    return name
                else:
                    return f'Unknown pot {name}'

        schema = strawberry.Schema(query=Query, mutation=Mutation)

        gql_api_server = Flask(__name__)
        gql_api_server.use_reloader=False
        gql_api_server.debug = False
        gql_api_server.config['TESTING'] = False

        gql_api_server.add_url_rule(
            "/graphql",
            view_func=GraphQLView.as_view("graphql_view", schema=schema),
        )
        return gql_api_server
