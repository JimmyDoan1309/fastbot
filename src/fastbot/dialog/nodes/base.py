import random
from typing import Text, List, Dict, Any, Callable, Union
from fastbot.models import Message, Step
from fastbot.dialog.context import ContextManager
from .status import NodeStatus, NodeResult


class BaseNode():
    def __init__(self, name: Text, **kwargs):
        self.name = name
        self.type = self.__class__.__name__
        self.next_node = kwargs.get('next_node', None)
        self.debug = kwargs.get('debug', False)
        self.config = kwargs

    def to_dict(self):
        return {'name': self.name}

    def on_enter(self, context: ContextManager) -> NodeResult:
        """
        Run once when node is enter. 
        Return:
            - NodeResult: do not run `on_message` method and return result to the controller
            or
            - None: continue to run `on_message`
        """
        pass

    def on_message(self, context: ContextManager) -> NodeResult:
        """
        Run every time recieve a message
        Return:
            - NodeResult
        """
        raise NotImplementedError("Child class must implement this.")

    def on_exit(self, context: ContextManager) -> NodeResult:
        """
        Run once when node is exit, right after `on_message` return NodeResult.status = Done. 
        Return:
            - NodeResult: override the NodeResult of `on_message`
            or
            - None: return `on_message` NodeResult
        """
        pass

    def run(self, context: ContextManager) -> NodeResult:

        status = context.get_status(self.name)
        if not status or status == NodeStatus.READY:
            context.set_status(self.name, NodeStatus.BEGIN)
            enter_result = self.on_enter(context)  # pylint: disable=assignment-from-no-return
            if enter_result:
                context.set_history(Step(self.name, status=enter_result.status))
                return enter_result

        message_result = self.on_message(context)

        if message_result.status == NodeStatus.DONE:
            exit_result = self.on_exit(context)  # pylint: disable=assignment-from-no-return
            context.set_status(self.name, NodeStatus.READY)
            if exit_result:
                context.set_history(Step(self.name, status=exit_result.status))
                return exit_result

        context.set_history(Step(action=self.name, status=message_result.status))
        return message_result
