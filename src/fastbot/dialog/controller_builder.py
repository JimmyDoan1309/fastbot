from .nodes import (
    TextResponse,
    IntentPrompt,
    InputsCollector,
    TextResultCondition,
    TextCondition
)
from .controller import DialogController
from fastbot.entity_extractors.pipeline_builder import ExtractorPipelineBuilder
from fastbot.utils.common import import_from_path
from fastbot.dialog.context import ContextManager
from fastbot.dialog.context.memory import MemoryContextManager
from typing import Text, List, Dict, Any, Optional, Union, Type
import json
import yaml
import sys
import os

registered_nodes = [
    TextResponse,
    IntentPrompt,
    InputsCollector,
    TextResultCondition,
    TextCondition,
]

node_mapping = {node.__name__: node for node in registered_nodes}


class DialogControlBuilder:
    def __init__(self, context: Optional[ContextManager] = MemoryContextManager(), **kwargs):
        self.context = context

    def load(self, path: Text, **kwargs) -> DialogController:
        """
        Path to the file contain the flow config
        """
        with open(path, 'r') as fp:
            if path.endswith('.json'):
                config = json.load(fp)
            elif path.endswith('.yaml') or path.endswith('.yml'):
                config = yaml.load(fp, Loader=yaml.FullLoader)
            else:
                raise Exception("Flow config must be .json or .yaml file")
        return self.loads(config, path=path, **kwargs)

    def loads(self, dialog_config: Dict[Text, Any], **kwargs) -> DialogController:
        path = kwargs.get('path')
        directory = os.path.abspath(os.path.dirname(path))
        if directory not in sys.path:
            sys.path.append(directory)

        nodes = dialog_config["nodes"]
        config = dialog_config.get("config", {})
        entities = dialog_config.get("entities", {})
        fallback_node_config = dialog_config.get("fallback")

        dialog_controller = DialogController(self.context)

        for node_config in nodes:
            if node_config['type'] == InputsCollector.__name__:
                node = self._create_inputs_collector_node(node_config, config, entities, InputsCollector)
            else:
                node_class = node_mapping.get(node_config['type'])
                if not node_class:
                    node_class = import_from_path(node_config['type'])

                if issubclass(node_class, InputsCollector):
                    node = self._create_inputs_collector_node(node_config, config, entities, node_class)
                else:
                    node = node_class(node_config['name'], **node_config.get('config', {}), next_node=node_config.get('next_node'))

            dialog_controller.add_node(node)
            if node_config.get('intent_trigger'):
                dialog_controller.add_intent_trigger(node_config['intent_trigger'], node)

        if fallback_node_config:
            fallback_node_class = node_mapping.get(fallback_node_config['type'])
            if not fallback_node_class:
                fallback_node_class = import_from_path(fallback_node_config['type'])

            fallback_node = fallback_node_class(
                fallback_node_config['name'],
                **fallback_node_config.get('config', {}),
                next_node=fallback_node_config.get('next_node'))

            dialog_controller.add_node(fallback_node)
            dialog_controller.set_fallback_node(fallback_node)

        return dialog_controller

    @staticmethod
    def _create_inputs_collector_node(
            node_config: Dict[Text, Any],
            config: Dict[Text, Any],
            entities: Dict[Text, Any],
            node_class: Type):

        node_entities = node_config['config'].pop('entities', [])
        entity_extractors = ExtractorPipelineBuilder(node_entities, entities, **config).build()
        escape_intent_action = node_config['config'].pop('escape_intent_action', [])
        validator = node_config['config'].pop('validator', None)
        inputs = node_config['config'].pop('inputs', {})

        if validator:
            validator = import_from_path(validator)

        return node_class(
            **node_config['config'],
            name=node_config['name'],
            inputs=inputs,
            entity_extractors=entity_extractors,
            escape_intent_action=escape_intent_action,
            validator=validator,
            next_node=node_config.get('next_node'))
