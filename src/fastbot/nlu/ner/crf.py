from . import NamedEntities
from fastbot.schema.nlu_data import NluData
from fastbot.models import Message, Entity
from typing import Dict, Text, Any, List, Optional, Tuple
import sklearn_crfsuite
import pickle


class CrfExtractor(NamedEntities):
    name = 'CrfExtractor'

    default = {
        'algorithm': 'lbfgs',
        'c1': 0.01,
        'c2': 0.01,
        'max_iterations': 100,
        'all_possible_transitions': True,
    }

    requires = ['SpacyPipeline']

    def __init__(self, config: Dict[Text, Any] = {}, confidence_threshold: int = 0.7, **kwargs):
        super().__init__(**kwargs)
        args = {**self.default, **config}
        self.model = kwargs.get("model", sklearn_crfsuite.CRF(**args))
        self.confidence_threshold = confidence_threshold

    def train(self, data: NluData):
        sents = [sample.nlu_cache.pos_tag for sample in data.all_samples]
        X = [self._sent2features(s, intent) for s, intent in zip(sents, data.all_intents)]
        y = [self._sent2labels(s) for s in sents]
        self.model.fit(X, y)

    def evaluate(self, test_data: NluData):
        pass

    def process(self, message: Message):
        feature = self._sent2features(message.nlu_cache.pos_tag, message.intent)
        pred = self.model.predict_marginals_single(feature)
        pred_score = [max(w.items(), key=lambda x:x[1]) for w in pred]
        message.entities.extend(self.convert_to_entity(pred_score, message))

    def convert_to_entity(self, result: List[Tuple[Text, float]], message: Message):

        entities = []
        entity_name = 'None'
        entity = {}

        def _add_entity():
            text = message.text[entity['start']: entity['end']]
            entities.append(Entity(
                entity_name,
                entity['start'],
                entity['end'],
                text,
                self.component_type,
                text=text,
                confidence=entity['confidence']
            ))

        for i, (feature, (result, score)) in enumerate(zip(message.nlu_cache.pos_tag, result), 1):
            if result.startswith('B'):
                if entity_name != 'None':
                    _add_entity()
                entity_name = '-'.join(result.split('-')[1:])
                entity = {
                    'entity': entity_name,
                    'start': feature['start'],
                    'end': feature['end'],
                    'extractor': 'CrfExtractor',
                    'confidence': score}
            elif result.startswith('O'):
                if entity_name != 'None':
                    _add_entity()
                entity_name = 'None'
                entity = {}
            elif result.startswith('I'):
                entity['end'] = feature['end']

            if i == len(result):
                if entity_name != 'None':
                    _add_entity()

        entities = [e for e in entities if e.confidence > self.confidence_threshold]
        return entities

    def _word2features(self, sent: List[Dict[Text, Text]], i: int, intent: Optional[Text] = None):
        word = sent[i]['word']
        features = {
            'bias': 1.0,
            'word.lower': word.lower(),
            'word.istitle': word.istitle(),
            'word.isupper': word.isupper(),
            'pos': sent[i]['pos'],
            'tag': sent[i]['tag'],
            'dep': sent[i]['dep'],
            'like_num': sent[i]['like_num'],
            'like_email': sent[i]['like_email'],
            'like_url': sent[i]['like_url'],
        }
        if i > 0:
            word_b = sent[i-1]['word']
            features.update({
                '-1:word.lower': word_b.lower(),
                '-1:word.istitle': word_b.istitle(),
                '-1:word.isupper': word_b.isupper(),
                '-1:pos': sent[i-1]['pos'],
                '-1:tag': sent[i-1]['tag'],
                '-1:dep': sent[i-1]['dep'],
                '-1:like_num': sent[i-1]['like_num'],
                '-1:like_email': sent[i-1]['like_email'],
                '-1:like_url': sent[i-1]['like_url'],
            })
        else:
            features['BOS'] = True

        if i < len(sent)-1:
            word_a = sent[i+1]['word']
            features.update({
                '+1:word.lower': word_a.lower(),
                '+1:word.istitle': word_a.istitle(),
                '+1:word.isupper': word_a.isupper(),
                '+1:pos': sent[i+1]['pos'],
                '+1:tag': sent[i+1]['tag'],
                '+1:dep': sent[i+1]['dep'],
                '+1:like_num': sent[i+1]['like_num'],
                '+1:like_email': sent[i+1]['like_email'],
                '+1:like_url': sent[i+1]['like_url'],
            })
        else:
            features['EOS'] = True
        if intent:
            features['intent'] = intent
        return features

    def _sent2features(self, sent: List[Dict], intent: Optional[Text] = None):
        return [self._word2features(sent, i, intent) for i in range(len(sent))]

    def _sent2labels(self, sent: List[Dict]):
        return [sent['ner'] for sent in sent]

    def get_metadata(self):
        return {
            'name': self.name,
            'type': self.component_type,
            'confidence_threshold': self.confidence_threshold,
        }

    def save(self, path: Text):
        with open(f'{path}/{self.name}.pkl', 'wb') as fp:
            pickle.dump(self.model, fp)

    @classmethod
    def load(cls, path: Text, metadata: Dict[Text, Any], **kwargs):
        with open(f'{path}/{metadata["name"]}.pkl', 'rb') as fp:
            model = pickle.load(fp)
        return cls(confidence_threshold=metadata["confidence_threshold"], model=model)
