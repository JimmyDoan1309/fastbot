from . import Vectorizer
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from typing import Text, List
import requests
import pickle
import numpy as np


class ExternalVectorizer(Vectorizer):
    """
    This Vectorizer call an external endpoint to retrieve the word vectors.
    which allow for decoupling between intepreter and any big pretrained word2vec framework 
        Ex: Fastext, Bert, Elmo, GPT, etc...

    Which mean:
        - Multiple bot can use the same SOTA word2vec without hoarding all the resources
        - Bot can be deployed to lower-end system that cannot handle something like BERT
            without sacrificing awesome benefit of SOTA word2vec
            Given other components is also not very resource-intensive

    Request format:
        json: {
            "raw_text": <original text>
            "processed_text": <text that has been preprocessed by other components>
            "tokenized_text": <List of word that has been tokenized in the text> 
        }

    Response:
        The Word2Vec server is expected to return a pickle serialized numpy array 
        (raw bytes) with shape [batch, word, dim]. And this Vectorizer will parse
        the result using:
            pickle.loads(bytes(response.content))
    """

    name = 'ExternalVectorizer'

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
