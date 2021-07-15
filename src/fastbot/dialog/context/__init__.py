from typing import Text, List, Dict, Any, Callable
from fastbot.models import Message, Response
import logging


log = logging.getLogger(__name__)


class TurnContext:
    def __init__(self, message: Message = None, **kwargs):
        self.message = message
        self.responses = []
        self.response_idx = 0

    def add_response(self, response: Response, **kwargs):
        response.watermark = f'{self.message.id}.{self.response_idx}'
        self.response_idx += 1
        self.responses.append(response)


class ContextManager:
    _id = None

    def __init__(self):
        self.dependencies = {}
        self.turn_context = TurnContext()

    def init(self, _id: Text = None):
        raise NotImplementedError()

    @classmethod
    def set_custom_response_function(cls, function: Callable):
        setattr(cls, 'response_function', function)

    def add_response(self, response: Response):
        response_function = getattr(self.__class__, 'response_function', self.turn_context.add_response)
        try:
            response_function(response, context=self)
        except Exception as e:
            log.error(e)
            self.turn_context.add_response(response)

    def create_turn_context(self, message: Message):
        raise NotImplementedError()

    def set_params(self, node_name: Text, value: Any):
        raise NotImplementedError()

    def set_result(self, node_name: Text, value: Any):
        raise NotImplementedError()

    def set_status(self, node_name: Text, value: int):
        raise NotImplementedError()

    def set_data(self, node_name: Text, value: Any):
        raise NotImplementedError()

    def get_params(self, node_name: Text, default: Any = None):
        raise NotImplementedError()

    def get_result(self, node_name: Text, default: Any = None):
        raise NotImplementedError()

    def get_status(self, node_name: Text, default: Any = None):
        raise NotImplementedError()

    def get_data(self, node_name: Text, default: Any = {}):
        raise NotImplementedError()

    def get_history(self):
        raise NotImplementedError()

    def is_done(self):
        raise NotImplementedError()

    def pop_callstack(self):
        raise NotImplementedError()

    def result(self, delete: bool = True):
        raise NotImplementedError()

    def load(self):
        raise NotImplementedError()

    def save(self):
        raise NotImplementedError()

    def restart(self):
        raise NotImplementedError()
