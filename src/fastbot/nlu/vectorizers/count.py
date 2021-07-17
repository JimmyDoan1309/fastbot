from . import Vectorizer
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from typing import Text, List, Dict, Any
from sklearn.feature_extraction.text import CountVectorizer as CVect
from scipy.sparse import hstack
import numpy as np
import pickle


class CountVectorizer(Vectorizer):
    name = 'CountVectorizer'

    def __init__(self, config: Dict[Text, Any] = {}, **kwargs):
        super().__init__(**kwargs)
        self.model = kwargs.get("model", CVect(**config))

    def train(self, data: NluData):
        texts = [sample.nlu_cache.processed_text for sample in data.all_samples]
        embeds = self.model.fit_transform(texts)
        for sample, embed in zip(data.all_samples, embeds):
            if sample.nlu_cache.sparse_embedding_vector != None:
                sample.nlu_cache.sparse_embedding_vector = hstack((
                    sample.nlu_cache.sparse_embedding_vector,
                    embed
                ))

            else:
                sample.nlu_cache.sparse_embedding_vector = embed

    def evaluate(self, test_data: NluData):
        for sample in test_data.all_samples:
            embed = self.model.transform([sample.nlu_cache.processed_text])[0]
            if sample.nlu_cache.sparse_embedding_vector != None:
                sample.nlu_cache.sparse_embedding_vector = hstack((
                    sample.nlu_cache.sparse_embedding_vector,
                    embed
                ))
            else:
                sample.nlu_cache.sparse_embedding_vector = embed

    def process(self, message: Message):
        embed = self.model.transform([message.nlu_cache.processed_text])[0]
        if message.nlu_cache.sparse_embedding_vector != None:
            message.nlu_cache.sparse_embedding_vector = hstack((
                message.nlu_cache.sparse_embedding_vector,
                embed
            ))
        else:
            message.nlu_cache.sparse_embedding_vector = embed

    def save(self, path: Text):
        with open(f'{path}/{self.name}.pkl', 'wb') as fp:
            pickle.dump(self.model, fp)

    @classmethod
    def load(cls, path: Text, metadata: Dict[Text, Any], **kwargs):
        with open(f'{path}/{metadata["name"]}.pkl', 'rb') as fp:
            model = pickle.load(fp)
        return cls(model=model)
