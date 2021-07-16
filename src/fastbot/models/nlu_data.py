from typing import Text, List, Dict, Any
from .cache import NluCache


class EntityAnnotation:
    def __init__(self, start: int, end: int, entity: Text):
        self.start = start
        self.end = end
        self.entity = entity

    @property
    def spacy_format(self):
        return (self.start, self.end, self.entity)


class Sample:
    def __init__(self, text: Text, entities: List[EntityAnnotation] = []):
        self.full_text = text
        self.entities = entities
        self.nlu_cache = NluCache(text)

    @property
    def spacy_format(self):
        return {"entities": [entity.spacy_format for entity in self.entities]}

    def __repr__(self):
        return self.full_text


class NluDataStatus:
    def __init__(self):
        self.is_tokenzied = False
        self.is_vectorized = False


class NluData:
    def __init__(self, intents: Dict[Text, List[Sample]]):
        self.intents = intents
        self.status = NluDataStatus()

    def clear_cache(self):
        for samples in self.intents.values():
            for sample in samples:
                sample.nlu_cache = NluCache(sample.full_text)

    @property
    def all_intents(self):
        return list(self.intents.keys())

    @property
    def all_samples(self):
        tmp = []
        for samples in self.intents.values():
            tmp += samples
        return tmp
