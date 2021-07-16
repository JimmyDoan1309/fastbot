from . import Processor
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from nltk import RegexpTokenizer
from typing import Text, Optional, Dict, Any


ALL = 'all'
CHARACTER = 'character'


class PunctuationRemover(Processor):
    name = 'PunctuationRemover'

    def __init__(self, puncs: Optional[Text] = None, **kwargs):
        super().__init__(**kwargs)
        self.puncs = puncs
        self.mode = CHARACTER
        self.tokenizer = None
        if not puncs:
            self.tokenizer = RegexpTokenizer(r'\w+')
            self.mode = ALL

    def _get_processed_text(self, text: Text):
        if self.mode == ALL:
            words = self.tokenizer.tokenize(text)
            return ' '.join(words)
        else:
            for p in self.puncs:
                text = text.replace(p, '')
            return text

    def train(self, data: NluData):
        for sample in data.all_samples:
            sample.nlu_cache.processed_text = self._get_processed_text(sample.nlu_cache.processed_text)

    def process(self, message: Message):
        message.nlu_cache.processed_text = self._get_processed_text(message.nlu_cache.processed_text)

    def get_metadata(self):
        return {
            'name': self.name,
            'type': self.component_type,
            'puncs': self.puncs
        }

    def save(self):
        pass

    @classmethod
    def load(cls, metadata: Dict[Text, Any], **kwargs):
        name = metadata.get('name', cls.name)
        puncs = metadata['puncs']
        return cls(puncs, name=name)
