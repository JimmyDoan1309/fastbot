from .cache import NluCache
from .entity import Entity
from typing import Dict, Text, Any
import uuid


class Message:
    def __init__(self, text: Text, **kwargs):
        self.text = text
        self.intent = None
        self.intents_ranking = []
        self.entities = []
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.config = kwargs
        self.nlu_cache = NluCache(text)

    def to_dict(self):
        return {
            'text': self.text,
            'intent': self.intent,
            'intents_ranking': self.intents_ranking,
            'entities': self.entities,
        }

    @classmethod
    def from_dict(cls, message: Dict[Text, Any]):
        msg = cls(message.get('text'))
        msg.intent = message.get('intent')
        msg.intents_ranking = message.get('intents_ranking', [])
        msg.entities = message.get('entities', [])
        return msg
