from . import Vectorizer
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from typing import Text, List
import requests
import pickle
import numpy as np


class FasttextVectorizer(Vectorizer):
    name = 'FasttextVectorizer'

    def __init__(self, endpoint: Text, **kwargs):
        super().__init__(**kwargs)
        self.endpoint = endpoint

    def _vectorized(self, data: List[List[Text]]):
        resp = requests.post(self.endpoint, json=data)
        if (resp.status_code != 200):
            raise Exception(f'Failed to connect to the server. code: {resp.status_code}')
        return pickle.loads(bytes(resp.content))

    def train(self, data: NluData):
        if data.status.is_vectorized:
            return

        for samples in data.intents.values():
            tokenized_samples = [sample.nlu_cache.tokenized_text for sample in samples]
            results = self._vectorized(tokenized_samples)
            for sample, result in zip(samples, results):
                sample.nlu_cache.dense_embedding_vector = result

        data.status.is_vectorized = True

    def process(self, message: Message):
        results = self._vectorized([message.nlu_cache.tokenized_text])
        message.nlu_cache.dense_embedding_vector = results[0]
