from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from fastbot.models.cache import NluCache
from .component import BaseComponent
from .classifiers import Classifier
from .registry import load_component
from typing import List, Text, Union, Dict, Any
import os
import shutil
import json
import re
import sys


class Interpreter:
    def __init__(self, components: List[BaseComponent] = [], **kwargs):
        self.pipeline_names = []
        self.pipeline = []
        for component in components:
            self.add_component(component)
        self.override_intent = kwargs.get("override_intent", False)
        self.override_intent_pattern = kwargs.get('override_intent_pattern', r'(?<=<)(\w|\.|-)+(?=>)')

    def verify_requirement(self, component: BaseComponent) -> bool:
        if not (set(component.requires).issubset(set(self.pipeline_names))):
            raise Exception(f'Component {component.component_type} requires {component.requires}!')
        return True

    def add_component(self, component: BaseComponent) -> None:
        if self.verify_requirement(component):
            self.pipeline.append(component)
            self.pipeline_names.append(component.component_type)

    def train(self, data: NluData, clear_cache=True) -> None:
        if (clear_cache):
            data.clear_cache()
        for component in self.pipeline:
            print(f'Start traning {component.name}')
            component.train(data)
            print(f'Done training {component.name}')

    def evaluate_classifiers(self, test_data: NluData, clear_cache=True) -> Dict[Text, Any]:
        if clear_cache:
            test_data.clear_cache()
        for component in self.pipeline:
            if not isinstance(component, Classifier):
                component.evaluate(test_data)
            else:
                results = component.evaluate(test_data)
                return results

    def _override_intent(self, message: Message) -> bool:
        match = re.search(self.override_intent_pattern, message.text)
        if match:
            message.intent = match.group()
            return True
        return False

    def process(self, message: Union[Message, str]) -> Dict[Text, Any]:
        if isinstance(message, str):
            message = Message(message)

        # Skip process if incomming message has a pre-polulated intent
        # This allow to setup intent trigger function that cannot be
        # access with text (ex: UI button)
        if message.intent:
            return message

        is_override = False
        if self.override_intent:
            is_override = self._override_intent(message)
        if not is_override:
            if message.nlu_cache.classifiers_output:
                message.nlu_cache.classifiers_output = {}
            for component in self.pipeline:
                component.process(message)
        return message

    def __iter__(self):
        for component in self.pipeline_names:
            yield component

    def get_component(self, name: Text):
        for component in self.pipeline:
            if component.component_type == name:
                return component
        return None

    def save(self, path: Text):
        path = os.path.abspath(path)
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)

        metadata = {
            'pipeline': [],
            'arguments': {
                'override_intent': self.override_intent,
                'override_intent_pattern': self.override_intent_pattern
            }
        }
        for component in self.pipeline:
            metadata['pipeline'].append(component.get_metadata())
            component.save(path)

        with open(f'{path}/metadata.json', 'w') as fp:
            json.dump(metadata, fp)

        return metadata

    @classmethod
    def load(cls, path: Text, **kwargs):
        if not path.endswith('/'):
            path += '/'

        directory = os.path.abspath(os.path.dirname(path))
        # This assume the model is saved 2 folders deep (/model/nlu) compare to
        # the bot code where all custom components is resigned.
        directory = '/'.join(directory.split('/')[:-2])

        if directory not in sys.path:
            sys.path.append(directory)

        with open(os.path.join(path, 'metadata.json'), 'r') as fp:
            metadata = json.load(fp)

        components = []
        for component_metadata in metadata['pipeline']:
            component_type = component_metadata['type']
            component = load_component(component_type, path, component_metadata)
            components.append(component)

        arguments = metadata.get('arguments', {})
        arguments.update(kwargs)
        return cls(components, **arguments)
