from . import (
    DucklingExtractor,
    ListExtractor,
    RegexExtractor,
    CompositeEntitiesExtractor,
    ExtractorPipeline,
)
from .unit_converter import UnitConverter
from fastbot.schema.entity import (
    MeasurementEntityConfigSchema,
    ListEntityConfigSchema,
    RegexEntityConfigSchema,
    CompositeEntityConfigSchema,
    CustomEntityConfigSchema,
)
from fastbot.models.entity import (
    ListEntityConfig,
    RegexEntityConfig,
    CompositeEntityConfig,
    CustomEntityConfig,
)
from fastbot.constants import DEFAULT_LANGUAGE
from fastbot.entity_extractors.constants import (
    DUCKLING_MEASURE_ENTITIES,
    DUCKLING_OTHER_ENTITIES,
    DUCKLING_TIME_ENTITIES,
    DUCKLING_ENTITIES,
    SPECIAL_ENTITIES,
    DUCKLING_ENDPOINT,
    ENTITY_PREFIX,
    DEFAULT_TEMP_UNIT,
    DEFAULT_TZ
)
from fastbot.utils.common import import_from_path
from typing import Text, List, Dict, Any
import re


class Extractor():
    DUCKLING = 'duckling'
    LIST = 'list'
    REGEX = 'regex'
    COMPOSITE = 'composite'
    CUSTOM = 'custom'


class ExtractorPipelineBuilder:
    def __init__(self,
                 entity_configs: List[Dict[Text, Any]],
                 based_on: Dict[Text, Any] = {},
                 **kwargs):
        self.language = kwargs.get('language', DEFAULT_LANGUAGE)
        self.duckling_endpoint = kwargs.get('duckling_endpoint', DUCKLING_ENDPOINT)
        self.default_temp_unit = kwargs.get('default_temp_unit', DEFAULT_TEMP_UNIT)
        self.default_timezone = kwargs.get('default_timezone', DEFAULT_TZ)

        self.entity_configs = entity_configs
        self.based_on = based_on

        self.entity_cache = {}
        self.extractor_cache = {}
        self.unit_cache = {}

    def build(self):
        self._create_pipeline(self.entity_configs, self.based_on)
        return self._build_pipeline()

    def _add_to_cache(self, key: Text, value: Any):
        if self.extractor_cache.get(key):
            self.extractor_cache[key].append(value)
        else:
            self.extractor_cache[key] = [value]

    def _create_pipeline(self, entity_configs: List[Dict[Text, Any]], based_on: [Dict[Text, Any]]):
        for entity in entity_configs:
            if entity['type'] == 'measurement':
                config = MeasurementEntityConfigSchema().load(entity['config'])
                self.unit_cache[config.measure] = config.default_unit
                self._add_to_cache(Extractor.DUCKLING, config.measure)

            elif entity['type'] in DUCKLING_OTHER_ENTITIES + DUCKLING_TIME_ENTITIES:
                self._add_to_cache(Extractor.DUCKLING, entity['type'])

            elif entity['type'] in [Extractor.LIST, Extractor.REGEX, Extractor.COMPOSITE, Extractor.CUSTOM]:
                self._create_other_entity_extractor(entity, based_on)

            else:
                entity_ref = based_on.get(entity['type'])
                if not entity_ref:
                    raise Exception(f'No reference found for entity: {entity["type"]}')
                self._create_other_entity_extractor(entity_ref, based_on)

    # def _create_special_entity_extractor(self, entity: Dict[Text, Any], based_on: Dict[Text, Any]):

    def _create_list_entity_extractor(self, config: ListEntityConfig):
        if self.entity_cache.get(config.name):
            return
        self.entity_cache[config.name] = 1

        self._add_to_cache(Extractor.LIST, ListExtractor(config))

    def _create_regex_entity_extractor(self, config: RegexEntityConfig):
        if self.entity_cache.get(config.name):
            return
        self.entity_cache[config.name] = 1

        self._add_to_cache(Extractor.REGEX, RegexExtractor(config))

    def _create_custom_entity_extractor(self, config: CustomEntityConfig):
        if self.entity_cache.get(config.name):
            return
        self.entity_cache[config.name] = 1

        extractor_class = import_from_path(config.extractor)
        self._add_to_cache(Extractor.CUSTOM, extractor_class(**config.arguments))

    def _create_composite_entity_extractor(self, config: CompositeEntityConfig, based_on: Dict[Text, Any]):
        if self.entity_cache.get(config.name):
            return
        self.entity_cache[config.name] = 1

        notation = fr'{ENTITY_PREFIX}[\w_]+(:[\w_]+)?'
        for pattern in config.patterns:
            for match in re.finditer(notation, pattern):
                match_text = match.group()
                sub_entity_name = match_text.split(':')[0][len(ENTITY_PREFIX):]
                if sub_entity_name in DUCKLING_ENTITIES:
                    self._add_to_cache(Extractor.DUCKLING, sub_entity_name)
                else:
                    entity_ref = based_on.get(sub_entity_name)
                    if not entity_ref:
                        raise Exception(f'No reference found for entity: {sub_entity_name}')
                    self._create_other_entity_extractor(entity_ref, based_on)
        self._add_to_cache(Extractor.COMPOSITE, CompositeEntitiesExtractor(config))

    def _create_other_entity_extractor(self, entity: Dict[Text, Any], based_on: Dict[Text, Any]):
        if entity['type'] == Extractor.LIST:
            config = ListEntityConfigSchema().load(entity.get('config'))
            self._create_list_entity_extractor(config)
        elif entity['type'] == Extractor.REGEX:
            config = RegexEntityConfigSchema().load(entity.get('config'))
            self._create_regex_entity_extractor(config)
        elif entity['type'] == Extractor.CUSTOM:
            config = CustomEntityConfigSchema().load(entity.get('config'))
            self._create_custom_entity_extractor(config)
        elif entity['type'] == Extractor.COMPOSITE:
            config = CompositeEntityConfigSchema().load(entity.get('config'))
            self._create_composite_entity_extractor(config, based_on)

    def _build_pipeline(self):

        # Composite extractors must be always at the end of the pipeline
        # to make sure all sub entities is available before compose them
        composite = []
        extractors = []

        for extractor, value in self.extractor_cache.items():
            if extractor == Extractor.DUCKLING:
                ext = DucklingExtractor(
                    list(set(value)),
                    endpoint=self.duckling_endpoint,
                    language=self.language,
                    timezone=self.default_timezone,
                    default_temp_unit=self.default_temp_unit)

                extractors.append(ext)
            elif extractor != Extractor.COMPOSITE:
                extractors.extend(value)
            else:
                composite.extend(value)

        extractors.extend(composite)

        pipeline = ExtractorPipeline(extractors, unit_map=self.unit_cache)
        return pipeline
