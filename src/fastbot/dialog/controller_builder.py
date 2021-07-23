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
from typing import Text, List, Dict, Any, Optional, Union
import json
import yaml

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
        return self.loads(config, **kwargs)

    def loads(self, dialog_config: Dict[Text, Any], **kwargs) -> DialogController:
        nodes = dialog_config["nodes"]
        config = dialog_config.get("config", {})
        entities = dialog_config.get("entities", {})
        fallback_node_config = dialog_config.get("fallback")

        dialog_controller = DialogController(self.context)

        for node_config in nodes:
            if node_config['type'] == InputsCollector.__name__:
                node_entities = node_config['config'].get('entities', [])
                escape_intent_action = node_config.get('escape_intent_action', [])
                entity_extractors = ExtractorPipelineBuilder(node_entities, entities, **config).build()
                node = InputsCollector(
                    node_config['name'],
                    node_config['config']['inputs'],
                    entity_extractors,
                    escape_intent_action,
                    next_node=node_config.get('next_node'))
            else:
                node_class = node_mapping.get(node_config['type'])
                if not node_class:
                    node_class = import_from_path(node_config['type'])

                node = node_class(
                    node_config['name'],
                    **node_config.get('config', {}),
                    next_node=node_config.get('next_node'))

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
