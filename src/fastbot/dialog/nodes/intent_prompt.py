from .base import BaseNode
from .status import NodeStatus, NodeResult
from fastbot.dialog.context import ContextManager
from fastbot.models.response import Response
from typing import Text, List
import random


class IntentPrompt(BaseNode):
    def __init__(self, name: Text, intents=List[Text], prompts=List[Text], **kwargs):
        super().__init__(name, **kwargs)
        self.intents = intents
        self.prompts = prompts

    def on_message(self, context: ContextManager):
        intent = context.turn_context.message.intent
        if intent in self.intents:
            context.set_result(self.name, intent)
            return NodeResult(NodeStatus.DONE, self.next_node)

        response = random.choice(self.prompts)
        context.add_response(Response('text', response))
        return NodeResult(NodeStatus.WAITING, self.name)
