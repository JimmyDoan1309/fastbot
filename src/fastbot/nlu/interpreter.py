from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from fastbot.models.cache import NluCache
from .component import BaseComponent
from .classifiers import Classifier
from .registry import load_component
from typing import List, Text
import os
import shutil
import json
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Interpreter:
    def __init__(self, components: List[BaseComponent] = []):
        self.pipeline = components

    def add_component(self, component: BaseComponent):
        self.pipeline.append(component)

    def train(self, data: NluData, clear_cache=True):
        if (clear_cache):
            data.clear_cache()
        for component in self.pipeline:
            print(f'Start traning {component.name}')
            component.train(data)
            print(f'Done training {component.name}')

    def evaluate_classifiers(self, test_data: NluData, clear_cache=True):
        if clear_cache:
            test_data.clear_cache()
        for component in self.pipeline:
            if not isinstance(component, Classifier):
                component.evaluate(test_data)
            else:
                results = component.evaluate(test_data)
                return results

    def parse(self, message: Message):
        if message.nlu_cache.classifiers_output:
            message.nlu_cache.classifiers_output = {}
        for component in self.pipeline:
            component.process(message)
        return message.to_dict()

    def save(self, path: Text):
        path = os.path.abspath(path)
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)

        metadata = {
            'pipeline': []
        }
        for component in self.pipeline:
            metadata['pipeline'].append(component.get_metadata())
            component.save(path)

        with open(f'{path}/metadata.json', 'w') as fp:
            json.dump(metadata, fp)

        return metadata

    @classmethod
    def load(cls, path: Text, **kwargs):
        with open(f'{path}/metadata.json', 'r') as fp:
            metadata = json.load(fp)

        components = []
        for component_metadata in metadata['pipeline']:
            component_type = component_metadata['type']
            component = load_component(component_type, path, component_metadata)
            components.append(component)

        return cls(components)
