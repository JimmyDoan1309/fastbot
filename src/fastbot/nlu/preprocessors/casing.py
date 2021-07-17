from . import Processor
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from typing import Text, Dict, Any

LOWER = 'lower'
UPPER = 'upper'


class CasingProcessor(Processor):
    name = 'CasingProcessor'

    def __init__(self, mode=LOWER, **kwargs):
        super().__init__(**kwargs)

        assert mode in [LOWER, UPPER]
        self.mode = mode

    def train(self, data: NluData):
        for sample in data.all_samples:
            if self.mode == LOWER:
                sample.nlu_cache.processed_text = sample.text.lower()
            else:
                sample.nlu_cache.processed_text = sample.text.upper()

    def process(self, message: Message):
        if self.mode == LOWER:
            message.nlu_cache.processed_text = message.text.lower()
        else:
            message.nlu_cache.processed_text = message.text.upper()

    def get_metadata(self):
        return {
            'name': self.name,
            'type': self.component_type,
            'mode': self.mode,
        }

    def save(self, path: Text):
        pass

    @classmethod
    def load(cls, path: Text, metadata: Dict[Text, Any], **kwargs):
        name = metadata.get('name', cls.name)
        mode = metadata['mode']
        return cls(mode, name=name)
