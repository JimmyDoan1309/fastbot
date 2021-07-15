from .interpreter import Interpreter
from .registry import get_component
from fastbot.schema.component import ComponentConfigSchema
from typing import Text, Dict, Any
import json
import yaml


class InterpreterBuilder:

    @classmethod
    def load(cls, path: Text):
        """
        Path to the file contain the nlu config
        """
        with open(path, 'r') as fp:
            if path.endswith('.json'):
                config = json.load(fp)
            elif path.endswith('.yaml') or path.endswith('.yml'):
                config = yaml.load(fp, Loader=yaml.FullLoader)
            else:
                raise Exception("NLU config must be .json or .yaml file")
        return cls.loads(config)

    @classmethod
    def loads(cls, config: Dict[Text, Any]):
        pipeline = config.get("pipeline", [])
        pipeline = ComponentConfigSchema(many=True).load(pipeline)
        interpreter = Interpreter()
        for component_config in pipeline:
            component_class = get_component(component_config.type)
            component = component_class(**component_config.arguements, name=component_config.name)
            interpreter.add_component(component)
        return interpreter
