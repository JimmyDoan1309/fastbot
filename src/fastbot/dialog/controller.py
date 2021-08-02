from .context import ContextManager, TurnContext
from .nodes.base import BaseNode
from .nodes.status import NodeStatus
from .policies import ActionPolicy
from fastbot.constants import DEFAULT_SESSION_TIMEOUT
from fastbot.nlu.interpreter import Interpreter
from fastbot.models import Message, Response, Step
from fastbot.constants import SHORT_CIRCUIT
from typing import Text, List, Dict, Any, Union, Optional
from copy import deepcopy


class DialogController:
    def __init__(self, context_type: ContextManager,
                 session_timeout_duration: float = DEFAULT_SESSION_TIMEOUT,
                 action_policy: Optional[ActionPolicy] = None):

        self._context_type = context_type

        self.nodes = {}
        self.intent_triggers = {}
        self.user_managers = {}
        self.fallback_node = None
        self.action_policy = action_policy
        self.session_timeout_duration = session_timeout_duration

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

    def inject_user_data(self, user_id: Text, key: Text, value: Any) -> None:
        user_context = self.get_user_context(user_id)
        user_context.user_data[key] = value

    def find_next_node(self, message: Message, context: ContextManager):
        node = self.intent_triggers.get(message.intent)
        if node:
            return node

        if self.action_policy:
            result = self.action_policy.process(message, context)
            if result.action:
                return result.action

        if self.fallback_node:
            return self.fallback_node

        return None

    def handle_message(self, message: Message, user_id: Text = 'default', turn_data: Dict[Text, Any] = {}) -> TurnContext:
        user_context = self.get_user_context(user_id)
        user_context.create_turn_context(message, turn_data)
        user_context.load()
        user_context.check_session_timeout(self.session_timeout_duration)
        user_context.update_session_timestamp()
        user_context.set_history(Step(intent=message.intent if message.intent else '<UNK>', message=message.__dict__()))

        # If callstack is empty
        if user_context.is_done():
            node = self.find_next_node(message, user_context)
            if node:
                user_context.set_callstack(node)
            else:
                return

        step = 1
        while not user_context.is_done():
            if step > SHORT_CIRCUIT:
                user_context.add_response(Response(f'Exceed {SHORT_CIRCUIT} steps without listening. Short Circuit!!!'))
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
