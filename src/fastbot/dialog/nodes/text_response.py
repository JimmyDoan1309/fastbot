from .base import BaseNode
from .status import NodeStatus, NodeResult
from fastbot.dialog.context import ContextManager
from fastbot.models.response import Response
from typing import Text, List
import random


class TextResponse(BaseNode):
    def __init__(self, name: Text, responses: List[Text], **kwargs):
        super().__init__(name, **kwargs)
        self.responses = responses

    def on_message(self, context: ContextManager) -> NodeResult:
        response = random.choice(self.responses)
        context.add_response(Response(response))
        return NodeResult(NodeStatus.DONE, self.next_node)
