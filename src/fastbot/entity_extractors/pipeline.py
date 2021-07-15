from .base import Extractor
from .composite_extractor import CompositeEntitiesExtractor
from .unit_converter import UnitConverter
from fastbot.models import Message, Entity
from typing import Text, List, Dict, Any
from .constants import DUCKLING_MEASURE_ENTITIES


class ExtractorPipeline:
    """
    List of entities extractor
    """

    def __init__(self, extractors: List[Extractor] = [], **kwargs):
        self.pipeline = extractors
        self.unit_map = kwargs.get('unit_map', None)
        self.unit_converter = UnitConverter()

    def add_extractor(self, extractor: Extractor):
        self.pipeline.append(extractor)

    def get_extractor_by_type(self, extractor_type: Text):
        for extractor in self.pipeline:
            if extractor.type == extractor_type:
                return extractor

    def get_extractor_by_name(self, extractor_name: Text):
        for extractor in self.pipeline:
            if extractor.name == extractor_name:
                return extractor

    def process(self, message: Message):
        for extractor in self.pipeline:
            if isinstance(extractor, CompositeEntitiesExtractor):
                message.entities = extractor.process(message)
            else:
                message.entities.extend(extractor.process(message))
        self._convert_unit(message)

    def _convert_unit(self, message: Message):
        if self.unit_map:
            for entity in message.entities:
                if entity.entity in DUCKLING_MEASURE_ENTITIES:
                    from_unit = entity.unit
                    to_unit = self.unit_map[entity.entity]
                    new_value = self.unit_converter.convert(entity.value, from_unit, to_unit, entity.entity)
                    entity.value = new_value
                    entity.unit = to_unit
