from .base import BaseNode
from .status import NodeStatus, NodeResult
from fastbot.dialog.context import ContextManager
from fastbot.models.response import Response
from typing import Text, List, Any, Text, Dict
import random


class TextCondition(BaseNode):
    """
    Basic Condition Node based on the raw text of the message.
    Params:
        - conditions: Mapping between message's text -> node name
    """

    def __init__(self, name: Text, conditions: Dict[Text, Text], **kwargs):
        super().__init__(name, **kwargs)
        self.conditions = conditions

    def on_message(self, context: ContextManager):
        message_text = context.turn_context.message.text
        next_node = self.conditions.get(message_text)
        if not next_node:
            next_node = self.next_node

        return NodeResult(NodeStatus.DONE, next_node)


class TextResultCondition(BaseNode):
    """
    Basic Condition Node based on the result of the previous node.
    This Condition Node assume the result of the previous node is a string.

    Params:
        - conditions: Mapping between result -> node name
    """

    def __init__(self, name: Text, conditions: Dict[Text, Text], **kwargs):
        super().__init__(name, **kwargs)
        self.conditions = conditions

    def on_message(self, context: ContextManager) -> NodeResult:
        prev_node_result = str(context.result(True))
        next_node = self.conditions.get(prev_node_result)
        if not next_node:
            next_node = self.next_node

        return NodeResult(NodeStatus.DONE, next_node)
