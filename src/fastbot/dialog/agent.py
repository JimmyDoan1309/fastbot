from fastbot.nlu.interpreter import Interpreter
from .controller_builder import DialogControlBuilder
from .context import ContextManager, TurnContext
from .context.memory import MemoryContextManager
from fastbot.models.message import Message
from typing import Optional, Union, Dict, Text, Any
from termcolor import colored


class Agent:
    def __init__(self,
                 interpreter_model_path: str,
                 flow_config_path: str,
                 context_manager: Optional[ContextManager] = MemoryContextManager(),
                 **kwargs):
        self.interpreter = Interpreter.load(interpreter_model_path, **kwargs)
        builder = DialogControlBuilder(context_manager)
        self.controller = builder.load(flow_config_path, **kwargs)

    def local_test(self, user_id: str = 'default') -> None:
        print(colored('Type "\q" to end the conversation', color='red', attrs=['bold']))
        raw = input(colored("User: ", color='green', attrs=['bold']))
        while raw != '\q':
            message = Message(raw)
            self.interpreter.process(message)
            result = self.controller.handle_message(message, user_id)
            for resp in result.responses:
                print(f"{colored('Bot:', color='blue', attrs=['bold'])} {resp.content}")
            raw = input(colored("User: ", color='green', attrs=['bold']))

    def process(self, message: Union[Message, str], user_id: str = 'default', turn_data: Dict[Text, Any] = {}) -> TurnContext:
        if isinstance(message, str):
            message = Message(message)
        self.interpreter.process(message)
        turn_context = self.controller.handle_message(message, user_id, turn_data)
        return turn_context
