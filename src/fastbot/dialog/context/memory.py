from typing import Text, List, Dict, Any, Union, Callable
from fastbot.models import Message, Response, Step
from . import ContextManager, TurnContext
from ..utils import create_user_conversation_id


class MemoryContextManager(ContextManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.callstack = []
        self.history = []
        self.node_results = {}
        self.node_params = {}
        self.node_status = {}
        self.node_data = {}

        self.user_data = {}
        self._user_data_manager = {}

    def init(self, user_id: Text, conversation_id: Text = None, user_data: Dict[Text, Any] = {}):
        assert isinstance(user_data, dict), 'user_data must be a json-serializable python dictionary'

        if not self._user_data_manager.get(user_id):
            self._user_data_manager[user_id] = {}

        if user_data:
            self._user_data_manager[user_id].update(user_data)

        ctx = self.__class__(
            user_id=user_id,
            conversation_id=conversation_id,
            response_function=self.response_function,
        )
        ctx.user_data = self._user_data_manager[user_id]
        return ctx

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
            if state.action is not None:
                result = self.node_results.get(state.action)
                if delete:
                    self.node_results.pop(state.action)
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

    def reset_node(self, node_name: Text):
        self.node_data.pop(node_name, None)
        self.node_results.pop(node_name, None)
        self.node_status.pop(node_name, None)

    def load(self):
        pass

    def save(self):
        pass

    def to_dict(self):
        return {
            'callstack': self.callstack,
            'history': [step.to_dict() for step in self.history],
            'node_params': self.node_params,
            'node_results': self.node_results,
            'node_data': self.node_data,
            'node_status': self.node_status,
            'timestamp': self.timestamp,
        }

    def update_user_data(self, user_id: Text, data: Dict[Text, Any] = {}):
        assert isinstance(data, dict), 'user_data must be a json-serializable python dictionary'

        if not self._user_data_manager.get(user_id):
            self._user_data_manager[user_id] = data
        else:
            self._user_data_manager[user_id].update(data)
