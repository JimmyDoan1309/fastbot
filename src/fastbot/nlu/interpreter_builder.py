from .interpreter import Interpreter
from .registry import get_component
from fastbot.schema.component import ComponentConfigSchema
from typing import Text, Dict, Any
import json
import yaml


class InterpreterBuilder:

    @classmethod
    def load(cls, path: Text, verbose=0):
        """
        Path to the file contain the nlu config
        """
        with open(path, 'r') as fp:
            if path.endswith('.json'):
                config = json.load(fp)
            elif path.endswith('.yaml') or path.endswith('.yml'):
                config = yaml.load(fp, Loader=yaml.FullLoader)
            else:
                raise Exception('NLU config must be .json or .yaml file')
        return cls.loads(config, verbose)

    @classmethod
    def loads(cls, config: Dict[Text, Any], verbose=0):
        pipeline = config.get('pipeline', [])
        arguments = config.get('arguments', {})
        pipeline = ComponentConfigSchema(many=True).load(pipeline)
        interpreter = Interpreter(**arguments)
        for component_config in pipeline:
            if verbose:
                print(f'Load component {component_config.name} [type: {component_config.type}]')
            component_class = get_component(component_config.type)
            component = component_class(**component_config.arguments, name=component_config.name)
            interpreter.add_component(component)
        if verbose:
            print('Create Interpreter successfully!')
        return interpreter
