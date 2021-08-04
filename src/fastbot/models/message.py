from .cache import NluCache
from .entity import Entity
from typing import Dict, Text, Any
import uuid
import json


class Message:
    def __init__(self, text: Text, **kwargs):
        self.text = text
        self.intent = None
        self.intents_ranking = []
        self.entities = []
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.config = kwargs
        self.nlu_cache = NluCache(text)

    def to_dict(self, include_ranking=False) -> Dict[Text, Any]:
        result = {
            'text': self.text,
            'intent': self.intent,
            'entities': [e.to_dict() for e in self.entities],
        }
        if include_ranking:
            result['intent_ranking'] = self.intents_ranking
        return result

    def __repr__(self) -> Text:
        return json.dumps(self.to_dict(True), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, message: Dict[Text, Any]) -> 'Message':
        msg = cls(message.get('text'))
        msg.intent = message.get('intent')
        msg.intents_ranking = message.get('intents_ranking', [])
        msg.entities = message.get('entities', [])
        return msg
