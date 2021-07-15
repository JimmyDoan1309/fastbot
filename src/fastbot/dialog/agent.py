from fastbot.nlu.interpreter import Interpreter
from fastbot.dialog.controller_builder import DialogControlBuilder
from fastbot.dialog.context import ContextManager, TurnContext
from fastbot.dialog.context.memory import MemoryContextManager
from fastbot.models.message import Message
from typing import Optional, Union


class Agent:
    def __init__(self, interpreter_model_path: str, flow_config_path: str, context_manager: Optional[ContextManager] = MemoryContextManager(), **kwargs):
        self.interpreter = Interpreter.load(interpreter_model_path)
        builder = DialogControlBuilder(context_manager)
        self.controller = builder.load(flow_config_path)

    def local_test(self, user_id: str = 'default'):
        raw = input("User: ")
        while raw != '\q':
            message = Message(raw)
            self.interpreter.parse(message)
            result = self.controller.handle_message(message, user_id)
            for resp in result.responses:
                print(f"Bot: {resp.content}")
            raw = input("User: ")

    def process(self, message: Union[Message, str], user_id: str = 'default'):
        if isinstance(message, str):
            message = Message(message)
        self.interpreter.parse(message)
        turn_context = self.controller.handle_message(message, user_id)
        return turn_context
