from .context import ContextManager, TurnContext
from .nodes.base import BaseNode
from .nodes.status import NodeStatus
from fastbot.nlu.interpreter import Interpreter
from fastbot.models import Message, Response
from fastbot.constants import SHORT_CIRCUIT
from typing import Text, List, Dict, Any, Union
from copy import deepcopy


class DialogController:
    def __init__(self, context_type: ContextManager):

        self._context_type = context_type

        self.nodes = {}
        self.intent_triggers = {}
        self.user_managers = {}
        self.fallback_node = None

    def add_node(self, node: BaseNode) -> None:
        self.nodes[node.name] = node

    def add_intent_trigger(self, intent: Text, node: Union[Text, BaseNode]) -> None:
        if isinstance(node, BaseNode):
            node = node.name
        self.intent_triggers[intent] = node

    def set_fallback_node(self, node: Union[Text, BaseNode]) -> None:
        """
        Default node run when callstack is empty and cannot find any triggered node
        """
        if isinstance(node, BaseNode):
            node = node.name
        self.fallback_node = node

    def get_user_context(self, user_id: Text) -> ContextManager:
        if not self.user_managers.get(user_id):
            self.user_managers[user_id] = self._context_type.init(user_id)

        return self.user_managers[user_id]

    def inject_dependency(self, user_id: Text, key: Text, value: Any) -> None:
        user_context = self.get_user_context(user_id)
        user_context.dependencies[key] = value

    def handle_message(self, message: Message, user_id: Text = 'default') -> TurnContext:
        user_context = self.get_user_context(user_id)
        user_context.create_turn_context(message)
        user_context.load()
        user_context.set_history('intent', message.intent, data=message.__dict__())

        # If callstack is empty
        if user_context.is_done():
            node = self.intent_triggers.get(message.intent)
            if node:
                user_context.set_callstack(node)
            else:
                if self.fallback_node:
                    user_context.set_callstack(self.fallback_node)
                else:
                    return

        step = 1
        while not user_context.is_done():
            if step > SHORT_CIRCUIT:
                user_context.add_response(Response('text', f'Exceed {SHORT_CIRCUIT} steps without listening. Short Circuit!!!'))
                user_context.restart()
                break

            action_name = user_context.pop_callstack()
            action = self.nodes[action_name]
            result = action.run(user_context)
            if result.next:
                user_context.set_callstack(result.next)

            step += 1

            if result.status == NodeStatus.DONE:
                continue
            elif result.status == NodeStatus.WAITING:
                break
            elif result.status == NodeStatus.RESTART:
                user_context.restart()
                break

        user_context.save()
        return user_context.turn_context
