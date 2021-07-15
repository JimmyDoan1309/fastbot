from . import Vectorizer
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from typing import Text, List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer as CVect
from scipy.sparse import hstack


class CountVectorizer(Vectorizer):
    name = 'CountVectorizer'

    def __init__(self, config: Dict[Text, Any] = {}, **kwargs):
        super().__init__(**kwargs)
        self.model = CVect(**config)

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
