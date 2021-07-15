from .base import SklearnClassifier
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from typing import Text, List, Dict, Any
from sklearn.neural_network import MLPClassifier


class NeuralNetClassifier(SklearnClassifier):
    name = 'NeuralNetClassifier'

    def __init__(self, config: Dict[Text, Any] = {}, **kwargs):
        super().__init__(**kwargs)
        self.model = MLPClassifier(**config)
