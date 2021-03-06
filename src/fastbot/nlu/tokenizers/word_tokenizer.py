from . import Tokenizer
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from typing import Text
import pickle
import re


class WordTokenizer(Tokenizer):
    name = 'WordTokenizer'

    def __init__(self, pattern: Text = r'\w+', **kwargs):
        super().__init__(**kwargs)
        self.tokenizer = re.compile(pattern)

    def train(self, data: NluData):
        for samples in data.intents.values():
            for sample in samples:
                sample.nlu_cache.tokens = [match for match in self.tokenizer.findall(sample.nlu_cache.processed_text)]

    def process(self, message: Message):
        message.nlu_cache.tokens = [match for match in self.tokenizer.findall(message.nlu_cache.processed_text)]
