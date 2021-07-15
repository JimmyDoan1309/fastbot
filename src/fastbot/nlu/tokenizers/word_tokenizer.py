from . import Tokenizer
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from nltk import RegexpTokenizer
from typing import Text
import pickle


class WordTokenizer(Tokenizer):
    name = 'WordTokenizer'

    def __init__(self, pattern: Text = r'\w+', **kwargs):
        super().__init__(**kwargs)
        self.tokenizer = RegexpTokenizer(pattern)

    def train(self, data: NluData):
        for samples in data.intents.values():
            for sample in samples:
                sample.nlu_cache.tokenized_text = self.tokenizer.tokenize(sample.nlu_cache.processed_text)

    def process(self, message: Message):
        message.nlu_cache.tokenized_text = self.tokenizer.tokenize(message.nlu_cache.processed_text)
