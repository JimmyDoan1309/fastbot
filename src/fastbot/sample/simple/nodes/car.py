from fastbot.dialog.nodes.base import BaseNode
from fastbot.dialog.context import ContextManager
from fastbot.dialog.nodes.status import NodeResult, NodeStatus
from fastbot.models.response import Response


class CarSearchConfirmation(BaseNode):
    def __init__(self, name: str, affirm: str, deny: str, **kwargs):
        super().__init__(name, **kwargs)
        self.affirm_action = affirm
        self.deny_action = deny

    def on_enter(self, context: ContextManager):
        result = context.result()
        resp = 'Searching For:\n'
        if result.get('car_year'):
            resp += f'\tYear: {result.get("car_year")}\n'
        if result.get('car_color'):
            resp += f'\tColor: {result.get("car_color")}\n'
        if result.get('car_brand'):
            resp += f'\tBrand: {result.get("car_brand")}\n'
        resp += f'\tModel: {result.get("car_model")}'
        context.add_response(Response(resp))

    def on_message(self, context: ContextManager):
        message_intent = context.turn_context.message.intent
        if message_intent == 'affirm':
            return NodeResult(NodeStatus.DONE, self.affirm_action)
        elif message_intent == 'deny':
            return NodeResult(NodeStatus.DONE, self.deny_action)

        context.add_response(Response('Do you want to search?'))
        return NodeResult(NodeStatus.WAITING, self.name)


class CarSearchAffirm(BaseNode):
    def on_message(self, context: ContextManager):
        # fake api call
        # import requests
        # resp = requests.get('...')
        context.add_response(Response('Fake api call'))
        return NodeResult(NodeStatus.DONE, self.next_node)


class CarSearchDeny(BaseNode):
    def on_message(self, context: ContextManager):
        context.add_response(Response('Sure, tell me if you need anything else.'))
        return NodeResult(NodeStatus.DONE, self.next_node)
