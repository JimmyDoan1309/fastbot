from typing import Text, List, Dict, Any
from .cache import NluCache


class Sample:
    def __init__(self, text: Text):
        self.full_text = text
        self.nlu_cache = NluCache(text)

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
