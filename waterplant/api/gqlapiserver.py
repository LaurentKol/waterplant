import logging
from typing import List

import strawberry
from flask import Flask
from strawberry.file_uploads import Upload
from strawberry.flask.views import GraphQLView as BaseGraphQLView

from waterplant.pot import Pot

class gql_api_server:
    def create_gql_api_server(pots: List[Pot]) -> Flask:

        def get_pots() -> List[Pot]:
            return pots
        # @strawberry.input
        # class FolderInput:
        #     files: typing.List[Upload]

        #TODO: clean-up this test
        @strawberry.type
        class Query:
            pots_str: str = f"{pots}"
            #pots_pot: typing.List[Pot] = strawberry.field(resolver=get_pots)

        @strawberry.type
        class Mutation:
            @strawberry.mutation
            def sprinkler_force_watering(self, name: str) -> str:
                pots_names = [d.name for d in pots]
                logging.info(pots_names)
                if(pot := next((x for x in pots if x.name == name), None)):
                    pot.sprinkler.set_force_next_watering(True)
                    return f'Forcing next watering sprinkler for {name}'
                else:
                    return f'Unknown pot {name}'

        schema = strawberry.Schema(query=Query, mutation=Mutation)

        class GraphQLView(BaseGraphQLView):
            def get_root_value(self) -> Query:
                return Query()


        gql_api_server = Flask(__name__)
        gql_api_server.use_reloader=False
        gql_api_server.debug = False

        gql_api_server.add_url_rule(
            "/graphql",
            view_func=GraphQLView.as_view("graphql_view", schema=schema),
        )
        return gql_api_server
