from .base import SklearnClassifier
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from typing import Text, List, Dict, Any
from sklearn.ensemble import RandomForestClassifier


class ForestClassifier(SklearnClassifier):
    name = 'RForestClassifier'

    def __init__(self, config: Dict[Text, Any] = {}, **kwargs):
        super().__init__(**kwargs)
        self.model = RandomForestClassifier(**config)
