from .base import Extractor
from fastbot.models import Message, Entity
from fastbot.models.entity import RegexEntityConfig
from typing import Dict, List, Text, Any, Union
import re


class RegexExtractor(Extractor):
    """
    Extract entities from messages using a regular expression
    """
    name = 'RegexExtractor'

    def __init__(self, entity_config: Union[Dict, RegexEntityConfig], **kwargs):
        super().__init__(**kwargs)

        if isinstance(entity_config, Dict):
            from fastbot.schema.entity import RegexEntityConfigSchema
            entity_config = RegexEntityConfigSchema().load(entity_config)

        self.entity_name = entity_config.name
        self.entity_patterns = entity_config.patterns

    def convert_to_entity(self, value: Any, start: int, end: int):
        return Entity(self.entity_name, start, end, value, self.name)

    def process(self, message: Message):
        text = message.text

        entities = []
        for pattern in self.entity_patterns:
            for m in re.finditer(pattern, text):
                start_index = m.start(0)
                end_index = m.end(0)
                entities.append(self.convert_to_entity(
                    m.group(),
                    start_index,
                    end_index,
                ))
        return entities
