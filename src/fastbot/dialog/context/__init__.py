from typing import Text, List, Dict, Any, Callable
from fastbot.models import Message, Response, Step
from fastbot.constants import DEFAULT_SESSION_TIMEOUT
import logging
from time import time


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
        self.user_data = {}
        self.timestamp = time()
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

    def set_history(self, step: Step):
        raise NotImplementedError()

    def get_params(self, node_name: Text, default: Any = None) -> Dict[Text, Any]:
        raise NotImplementedError()

    def get_result(self, node_name: Text, default: Any = None) -> Dict[Text, Any]:
        raise NotImplementedError()

    def get_status(self, node_name: Text, default: Any = None) -> Dict[Text, Any]:
        raise NotImplementedError()

    def get_data(self, node_name: Text, default: Any = {}) -> Dict[Text, Any]:
        raise NotImplementedError()

    def get_history(self) -> List[Step]:
        raise NotImplementedError()

    def is_done(self) -> bool:
        raise NotImplementedError()

    def pop_callstack(self) -> Text:
        raise NotImplementedError()

    def result(self, delete: bool = True):
        raise NotImplementedError()

    def load(self) -> None:
        raise NotImplementedError()

    def save(self) -> None:
        raise NotImplementedError()

    def restart(self) -> None:
        raise NotImplementedError()

    def check_session_timeout(self, timeout_in: float = DEFAULT_SESSION_TIMEOUT) -> None:
        current = time()/3600
        last_message = self.timestamp/3600
        if (current - last_message) > timeout_in:
            self.restart()

    def update_session_timestamp(self) -> None:
        self.timestamp = time()
