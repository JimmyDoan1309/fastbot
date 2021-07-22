from typing import Text, List, Dict, Any, Union, Callable
from fastbot.models import Message, Response, Step
from . import ContextManager, TurnContext


class MemoryContextManager(ContextManager):
    def __init__(self):
        super().__init__()
        self.callstack = []
        self.history = []
        self.node_results = {}
        self.node_params = {}
        self.node_status = {}
        self.node_data = {}

    def init(self, _id: Text = None):
        return self.__class__()

    def create_turn_context(self, message: Message):
        self.turn_context = TurnContext(message)

    def set_params(self, node_name: Text, value: Any):
        self.node_params[node_name] = value

    def set_result(self, node_name: Text, value: Any):
        self.node_results[node_name] = value

    def set_status(self, node_name: Text, value: int):
        self.node_status[node_name] = value

    def set_data(self, node_name: Text, value: Any):
        self.node_data[node_name] = value

    def set_callstack(self, node_name: Union[Text, List[Text]]):
        if isinstance(node_name, List):
            self.callstack.extend(node_name)
        else:
            self.callstack.append(node_name)

    def set_history(self, step: Step):
        self.history.append(step)

    def get_params(self, node_name: Text, default: Any = None):
        return self.node_params.get(node_name, default)

    def get_result(self, node_name: Text, default: Any = None):
        return self.node_results.get(node_name, default)

    def get_status(self, node_name: Text, default: Any = None):
        return self.node_status.get(node_name, default)

    def get_data(self, node_name: Text, default: Any = {}):
        return self.node_data.get(node_name, default)

    def get_history(self):
        return self.history

    def is_done(self):
        return not bool(self.callstack)

    def result(self, delete: bool = True):
        for state in reversed(self.history):
            if state['type'] == 'action':
                result = self.node_results.get(state['name'])
                if delete:
                    self.node_results.pop(state['name'])
                return result
        return None

    def pop_callstack(self):
        return self.callstack.pop()

    def restart(self, user_data=False):
        self.callstack = []
        self.history = []
        self.node_results = {}
        self.node_params = {}
        self.node_status = {}
        self.node_data = {}
        if user_data:
            self.user_data = {}

    def load(self):
        pass

    def save(self):
        pass

    def json(self):
        return {
            'callstack': self.callstack,
            'history': [step.__dict__() for step in self.history],
            'node_params': self.node_params,
            'node_results': self.node_results,
            'node_data': self.node_data,
            'node_status': self.node_status,
            'timestamp': self.timestamp,
        }
