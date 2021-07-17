from .. import Classifier
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from sklearn.metrics import accuracy_score, f1_score
import numpy as np


class SklearnClassifier(Classifier):
    name = 'SklearnClassifier'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._reduce_method = kwargs.get('reduce_method', 'mean')
        assert self._reduce_method in ['mean', 'sum'], "reduce method can only be `mean` or `sum`"
        # self._use_vector = kwargs.get('use_vector', 'dense')
        # assert self._use_vector in ['dense', 'sparse'], "can only choose between `dense` or `sparse` vector"
        self.model = None

    def _reduce(self, words_embedding: np.ndarray):
        """
        Because Sklearn model can only handle 1-D vector with shape (embed_dims) 
        while default sentence get encode as 2-D vector with shape (n_word, embed_dims)

        This function caculate the sentence embedding as average or sum of words' embedding

        Parameters:
            words_embedding: 2-D numpy array with shape (n_word, embed_dims)
        """
        if len(words_embedding.shape) == 1:
            return words_embedding
        if self._reduce_method == 'mean':
            return words_embedding.mean(axis=0)
        else:
            return words_embedding.sum(axis=0)

    def _concat_dense_sparse(self, dense_vector: np.ndarray, sparse_vector: any):
        if sparse_vector is not None and dense_vector is not None:
            return np.concatenate((self._reduce(dense_vector), sparse_vector.toarray()[0]), axis=0)
        elif sparse_vector is not None:
            return sparse_vector.toarray()[0]
        elif dense_vector is not None:
            return self._reduce(dense_vector)

    def _prepared_data(self, data: NluData, create_label_mapping: bool = False):
        if create_label_mapping:
            self._create_label_mapping(data)

        X = [self._concat_dense_sparse(
            sample.nlu_cache.dense_embedding_vector,
            sample.nlu_cache.sparse_embedding_vector)
            for sample in data.all_samples]
        y = [self.intent2idx[intent] for intent in data.all_intents]
        return X, y

    def train(self, data: NluData):
        X, y = self._prepared_data(data, True)
        self.model.fit(X, y)

    def predict_test_data(self, test_data: NluData):
        X, y_true = self._prepared_data(test_data)
        y_pred = self.model.predict_proba(X)
        return y_true, y_pred

    def evaluate(self, test_data: NluData):
        y_true, y_pred = self.predict_test_data(test_data)
        y_pred = np.argmax(y_pred, axis=-1)

        texts = [sample.text for sample in test_data.all_samples]

        misses = []
        for text, pred, true in zip(texts, y_pred, y_true):
            if (pred != true):
                misses.append({
                    'text': text,
                    'true': self.idx2intent[true],
                    'pred': self.idx2intent[pred],
                })

        results = {
            "scores": {
                'acc': accuracy_score(y_true, y_pred),
                'f1': f1_score(y_true, y_pred, average='weighted')
            },
            "misses": misses,
            'results': {
                'y_pred': [self.idx2intent[pred] for pred in y_pred],
                'y_true': [self.idx2intent[true] for true in y_true],
            }
        }
        return results

    def predict(self, message: Message):
        embed = self._concat_dense_sparse(message.nlu_cache.dense_embedding_vector, message.nlu_cache.sparse_embedding_vector)
        probs = self.model.predict_proba([embed])[0]

        ranking = []
        for i, prob in enumerate(probs):
            ranking.append({'name': self.idx2intent[i], 'score': prob})
        ranking.sort(key=lambda i: i['score'], reverse=True)

        return ranking

    def process(self, message: Message):
        ranking = self.predict(message)

        message.nlu_cache.classifiers_output[self.name] = ranking
        message.intents_ranking = ranking

        # Check intent threshold
        if (message.intents_ranking[0]['score'] > self.confident_threshold and
                message.intents_ranking[0]['score'] - message.intents_ranking[1]['score'] > self.ambiguity_threshold):
            message.intent = message.intents_ranking[0]['name']
