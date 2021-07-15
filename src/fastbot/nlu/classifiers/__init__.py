from fastbot.nlu.component import BaseComponent
from fastbot.nlu.constants import NLU_CONFIDENT_THRESHOLD, NLU_AMBIGUITY_THRESHOLD
from fastbot.schema.nlu_data import NluData

class Classifier(BaseComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.confident_threshold = kwargs.get('confident_threshold', NLU_CONFIDENT_THRESHOLD)
        self.ambiguity_threshold = kwargs.get('ambiguity_threshold', NLU_AMBIGUITY_THRESHOLD)

    def _create_label_mapping(self, data: NluData):
        self.intents = data.all_intents
        self.intent2idx = {intent: idx for idx, intent in enumerate(self.intents)}
        self.idx2intent = {idx: intent for intent, idx in self.intent2idx.items()}
        self.number_of_intent = len(self.intents)

    def predict(self):
        raise NotImplementedError('Subclass must implement this')
