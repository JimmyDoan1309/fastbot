from . import Tokenizer
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from pyvi.ViTokenizer import tokenize as vi_tokenize
from nltk import RegexpTokenizer
from typing import Text
import pickle


class VietnameseTokenizer(Tokenizer):
    name = 'VietnameseTokenizer'

    def __init__(self, pattern: Text = r'\w+', **kwargs):
        super().__init__(**kwargs)
        self.tokenizer = RegexpTokenizer(pattern)

    def train(self, data: NluData):
        for samples in data.intents.values():
            for sample in samples:
                processed_text = vi_tokenize(sample.nlu_cache.processed_text)
                sample.nlu_cache.tokenized_text = self.tokenizer.tokenize(processed_text)

    def process(self, message: Message):
        processed_text = vi_tokenize(message.nlu_cache.processed_text)
        message.nlu_cache.tokenized_text = self.tokenizer.tokenize(processed_text)

