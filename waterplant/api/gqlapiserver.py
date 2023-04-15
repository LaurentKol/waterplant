from datetime import datetime
import logging
from typing import List

import strawberry
from flask import Flask
from strawberry.flask.views import GraphQLView
from apscheduler.schedulers.base import BaseScheduler

from waterplant.pot import Pot
from waterplant.jobs.water import water

class GqlApiServer:
    def create_gql_api_server(pots: List[Pot], scheduler: BaseScheduler) -> Flask:

        @strawberry.type
        class Pot:
            name: str
            dryness_threshold: int
            sprinkler_last_watering: datetime
            sprinkler_watering_now: bool


        @strawberry.type
        class Query:
            @strawberry.field
            def pot(self, info: strawberry.types.Info, name: str) -> Pot:
                pot = [pot for pot in pots if pot.name == name].pop()
                pot.sprinkler_last_watering = pot.sprinkler.last_watering
                pot.sprinkler_watering_now = False
                return pot


        @strawberry.type
        class Mutation:
            @strawberry.mutation
            def sprinkler_force_watering(self, name: str) -> str:
                if(pot := next((p for p in pots if p.name == name), None)):
                    logging.info(f'[GQL] Got force watering {name}, scheduling watering job')
                    scheduler.add_job(water, kwargs={'pot': pot}, id=f'watering-{pot.name}', misfire_grace_time=60, coalesce=True, executor='watering')
                    return name
                else:
                    return f'Unknown pot {name}'

        schema = strawberry.Schema(query=Query, mutation=Mutation)

        class MyGraphQLView(GraphQLView):
            pass

        gql_api_server = Flask(__name__)
        gql_api_server.use_reloader=False
        gql_api_server.debug = False
        gql_api_server.config['ENV'] = 'development'

        gql_api_server.add_url_rule(
            "/graphql",
            view_func=GraphQLView.as_view("graphql_view", schema=schema),
        )
        return gql_api_server
