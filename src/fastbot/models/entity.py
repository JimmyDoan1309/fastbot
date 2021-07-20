from typing import List, Text, Dict, Any, Optional
import json


class Entity:
    def __init__(self,
                 entity: Text,
                 start: int, end: int,
                 value: Optional[Any] = None,
                 extractor: Optional[Any] = None,
                 unit: Optional[Text] = None,
                 text: Optional[Text] = None,
                 confidence: Optional[float] = 1.0,
                 role: Optional[Text] = None,
                 from_entity: Optional[Text] = None,
                 ):
        self.entity = entity
        self.start = start
        self.end = end
        self.value = value
        self.unit = unit
        self.text = text
        self.extractor = extractor
        self.confidence = confidence
        self.role = role
        self.from_entity = from_entity

    def __dict__(self):
        body = {
            'entity': self.entity,
            'value': self.value,
            'start': self.start,
            'end': self.end,
            'extractor': self.extractor,
            'confidence': self.confidence
        }
        if self.unit:
            body['unit'] = self.unit
        if self.text:
            body['text'] = self.text
        if self.from_entity:
            body['from_entity'] = self.from_entity
        if self.role:
            body['role'] = self.role
        return body

    def __repr__(self):
        return json.dumps(self.__dict__(), ensure_ascii=False, indent=2)


class MeasurementEntityConfig:
    def __init__(self, measure: Text, default_unit: Text):
        self.measure = measure
        self.default_unit = default_unit


class ListEntityItem:
    def __init__(self, name: Text, code: Optional[Text] = None, synonyms: List[Text] = []):
        self.name = name
        self.code = code
        self.synonyms = synonyms


class ListEntityConfig:
    def __init__(self, name: Text,
                 values: List[ListEntityItem],
                 case_sensitive: bool = True,
                 fuzzy_match: bool = False,
                 fuzzy_match_threshold: float = 70.0,
                 fuzzy_match_min_search_length: int = 5):
        self.name = name
        self.values = values
        self.case_sensitive = case_sensitive
        self.fuzzy_match = fuzzy_match
        self.fuzzy_match_threshold = fuzzy_match_threshold
        self.fuzzy_match_min_search_length = fuzzy_match_min_search_length


class RegexEntityConfig:
    def __init__(self, name: Text, patterns: List[Text] = []):
        self.name = name
        self.patterns = patterns


class CompositeEntityConfig:
    def __init__(self, name: Text, patterns: List[Text] = []):
        self.name = name
        self.patterns = patterns


class CustomEntityConfig:
    def __init__(self, name: Text, extractor: Text, arguments: Dict[Text, Any] = {}):
        self.name = name
        self.extractor = extractor
        self.arguments = arguments
