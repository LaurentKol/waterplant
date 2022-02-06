import logging
from typing import List

import strawberry
from flask import Flask
from strawberry.file_uploads import Upload
from strawberry.flask.views import GraphQLView as BaseGraphQLView

from waterplant.pot import Pot

class GqlApiServer:
    def create_gql_api_server(pots: List[Pot]) -> Flask:

        @strawberry.type
        class Pot:
            name: str
            dryness_threshold: int
            max_watering_frequency_seconds: int

        def get_pots() -> List[Pot]:
            return pots
        # @strawberry.input
        # class FolderInput:
        #     files: typing.List[Upload]

        #TODO: clean-up this test
        @strawberry.type
        class Query:
            pots: List[Pot] = strawberry.field(resolver=get_pots)

        @strawberry.type
        class Mutation:
            @strawberry.mutation
            def sprinkler_force_watering(self, name: str) -> str:
                if(pot := next((p for p in pots if p.name == name), None)):
                    pot.sprinkler.set_force_next_watering(True)
                    logging.info(f'[GQL] Got force watering {name}')
                    return name
                else:
                    return f'Unknown pot {name}'

        schema = strawberry.Schema(query=Query, mutation=Mutation)

        class GraphQLView(BaseGraphQLView):
            def get_root_value(self) -> Query:
                return Query()


        gql_api_server = Flask(__name__)
        gql_api_server.use_reloader=False
        gql_api_server.debug = False
        gql_api_server.config['ENV'] = 'development'

        gql_api_server.add_url_rule(
            "/graphql",
            view_func=GraphQLView.as_view("graphql_view", schema=schema),
        )
        return gql_api_server
