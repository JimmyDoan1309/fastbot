from typing import Text, List, Dict, Any
from .cache import NluCache
from .entity import Entity


TRAIN_DATA = 'TrainData'


class Sample:
    def __init__(self, text: Text, entities: List[Entity] = []):
        self.text = text
        self.entities = entities
        self.intent = None
        self.nlu_cache = NluCache(text)
        for e in self.entities:
            e.value = self.text[e.start:e.end]
            e.extractor = TRAIN_DATA

    def __repr__(self):
        return self.text


class NluDataStatus:
    def __init__(self):
        self.is_tokenzied = False
        self.is_vectorized = False


class NluData:
    def __init__(self, intents: Dict[Text, List[Sample]]):
        self.intents = intents
        self.status = NluDataStatus()
        for intent, samples in self.intents.items():
            for sample in samples:
                sample.intent = intent

    def clear_cache(self):
        for samples in self.intents.values():
            for sample in samples:
                sample.nlu_cache = NluCache(sample.text)

    @property
    def intent_names(self):
        return list(self.intents.keys())

    @property
    def all_intents(self):
        tmp = []
        for intent, samples in self.intents.items():
            tmp += [intent]*len(samples)
        return tmp

    @property
    def all_samples(self):
        tmp = []
        for samples in self.intents.values():
            tmp += samples
        return tmp
