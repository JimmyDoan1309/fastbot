from typing import Text, List, Dict, Any, Callable
from fastbot.models import Message, Response, Step
from fastbot.constants import DEFAULT_SESSION_TIMEOUT
import logging
from time import time
from ..utils import create_user_conversation_id


log = logging.getLogger(__name__)


class TurnContext:
    def __init__(self, message: Message = None, turn_data: Dict[Text, Any] = {}):
        self.message = message
        self.turn_data = turn_data
        self.responses = []
        self.response_idx = 0

    def add_response(self, response: Response, **kwargs):
        response.watermark = f'{self.message.id}.{self.response_idx}'
        self.response_idx += 1
        self.responses.append(response)


class ContextManager:
    def __init__(self, **kwargs):
        self.timestamp = time()
        self.turn_context = TurnContext()
        self.response_function = kwargs.get('response_function')
        self.user_id = kwargs.get('user_id') or 'default'
        self.conversation_id = kwargs.get('conversation_id')

    def add_response(self, response: Response):
        try:
            if self.response_function:
                self.response_function(response, context=self)
            else:
                self.turn_context.add_response(response)
        except Exception as e:
            log.error(e)
            self.turn_context.add_response(response)

    def init(self, user_id: Text = None, conversation_id: Text = None, user_data: Dict[Text, Any] = {}):
        raise NotImplementedError()

    def create_turn_context(self, message: Message, turn_data: Dict[Text, Any] = {}):
        self.turn_context = TurnContext(message, turn_data)

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

    def load(self, **kwargs) -> None:
        raise NotImplementedError()

    def save(self, **kwargs) -> None:
        raise NotImplementedError()

    def restart(self) -> None:
        raise NotImplementedError()

    def reset_node(self, node_name: Text) -> None:
        raise NotImplementedError()

    def update_user_data(self, user_id: Text, data: Dict[Text, Any] = {}) -> None:
        raise NotImplementedError()

    def check_session_timeout(self, timeout_in: float = DEFAULT_SESSION_TIMEOUT) -> None:
        current = time()/3600
        last_message = self.timestamp/3600
        if (current - last_message) > timeout_in:
            self.restart()

    def update_session_timestamp(self) -> None:
        self.timestamp = time()

    @property
    def _id(self):
        return create_user_conversation_id(self.user_id, self.conversation_id)
