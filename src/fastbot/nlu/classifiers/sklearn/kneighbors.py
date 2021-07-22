from .base import SklearnClassifier
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from typing import Text, List, Dict, Any
from sklearn.neighbors import KNeighborsClassifier


class KnnClassifier(SklearnClassifier):
    name = 'KnnClassifier'

    default = {
        'weights': 'distance'
    }

    def __init__(self, config: Dict[Text, Any] = {}, **kwargs):
        super().__init__(**kwargs)
        args = {**self.default, **config}
        self.model = kwargs.get('model', KNeighborsClassifier(**args))
