from fastbot.dialog.nodes.base import BaseNode
from fastbot.dialog.context import ContextManager
from fastbot.dialog.nodes.status import NodeResult, NodeStatus
from fastbot.models.response import Response
import requests


class GetJokeResponse(BaseNode):
    url = "https://official-joke-api.appspot.com/jokes/programming/random"

    def on_message(self, context: ContextManager):
        resp = requests.get(self.url, timeout=3)
        if resp.status_code == 200:
            joke = resp.json()[0]
            setup = joke['setup']
            punchline = joke['punchline']
            context.add_response(Response(setup))
            context.add_response(Response(punchline))
        else:
            text = "Fail to fetch joke from external api"
            context.add_response(Response(text))
        return NodeResult(NodeStatus.DONE, self.next_node)


class GetFactResponse(BaseNode):
    url = "https://uselessfacts.jsph.pl/random.json?language=en"

    def on_message(self, context: ContextManager):
        resp = requests.get(self.url, params={"format": "json"}, timeout=3)
        if resp.status_code == 200:
            text = resp.json()['text']
        else:
            text = "Fail to fetch fact from external api"
        context.add_response(Response(text))
        return NodeResult(NodeStatus.DONE, self.next_node)
