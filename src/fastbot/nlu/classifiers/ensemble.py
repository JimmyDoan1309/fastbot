from . import Classifier
import numpy as np
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from typing import Text, List, Dict, Any
from sklearn.metrics import accuracy_score, f1_score


class EnsembleClassifier(Classifier):
    name = 'EnsembleClassifier'

    def __init__(self, classifiers: List[Classifier], strategy: Text = 'max', classifier_weights: List[float] = None, **kwargs):
        super().__init__(**kwargs)
        assert strategy in ['average', 'max'], "strategy can only be `max` or `average`"

        if strategy == 'average':
            if (classifier_weights):
                assert len(classifiers) == len(classifier_weights), "Mismatch size between `classifiers` and `classifier_weights`"
                assert sum(classifier_weights) == 1, "Sum of classifier_weights must be 1.0"
            else:
                classifier_weights = [1/len(classifiers)]*len(classifiers)

        self.classifiers = classifiers
        self.strategy = strategy
        self.weights = classifier_weights

    def train(self, data: NluData):
        self._create_label_mapping(data)
        for c in self.classifiers:
            print(f'Start training {c.name}')
            c.train(data)
            print(f'Done training {c.name}')

    def evaluate(self, test_data: NluData):
        y_true, y_pred = self.predict_test_data(test_data)
        y_pred = np.argmax(y_pred, axis=-1)
        texts = [sample.full_text for sample in test_data.all_samples]

        misses = []
        for text, pred, true in zip(texts, y_pred, y_true):
            if (pred != true):
                misses.append({
                    'text': text,
                    'true': self.idx2intent[true],
                    'pred': self.idx2intent[pred],
                })

        results = {
            'scores': {
                'acc': accuracy_score(y_true, y_pred),
                'f1': f1_score(y_true, y_pred, average='weighted')
            },
            'misses': misses,
            'results': {
                'y_pred': [self.idx2intent[pred] for pred in y_pred],
                'y_true': [self.idx2intent[true] for true in y_true],
            }
        }

        return results

    def predict_test_data(self, test_data: NluData):
        classifiers_outputs = {}
        for c in self.classifiers:
            y_true, y_pred = c.predict_test_data(test_data)
            classifiers_outputs[c.name] = y_pred

        y_pred = []
        for i in range(len(test_data.all_samples)):
            if self.strategy == 'average':
                avg_pred = np.zeros((len(test_data.all_intents)))
                for j, pred in enumerate(classifiers_outputs.values()):
                    avg_pred += pred[i] * self.weights[j]
                y_pred.append(avg_pred)

            elif self.strategy == 'max':
                max_confidence = 0
                max_pred = np.zeros((len(test_data.all_intents)))
                for pred in classifiers_outputs.values():
                    if np.max(pred[i]) > max_confidence:
                        max_confidence = np.max(pred[i])
                        max_pred = pred[i]
                y_pred.append(max_pred)

        y_pred = np.asarray(y_pred)
        return y_true, y_pred

    def _process_classifers_output(self, classifiers_output: Dict[Text, Any]):
        intents = {}
        if self.strategy == 'average':
            # Scaled classifiers' results base on classifiers' weights
            for i, intents_ranking in enumerate(classifiers_output.values()):
                for intent in intents_ranking:
                    if (not intents.get(intent['name'])):
                        intents[intent['name']] = intent['score'] * self.weights[i]
                    else:
                        intents[intent['name']] += intent['score'] * self.weights[i]

        elif self.strategy == 'max':
            for i, (classifier, intents_ranking) in enumerate(classifiers_output.items()):
                for intent in intents_ranking:
                    if (not intents.get(intent['name'])):
                        intents[intent['name']] = {
                            'score': intent['score'],
                            'classifier': classifier
                        }
                    else:
                        if (intent['score'] > intents[intent['name']]['score']):
                            intents[intent['name']] = {
                                'score': intent['score'],
                                'classifier': classifier
                            }

        return intents

    def predict(self, message: Message):
        classifiers_output = {}
        for c in self.classifiers:
            c_ranking = c.predict(message)
            message.nlu_cache.classifiers_output[c.name] = c_ranking
            classifiers_output[c.name] = c_ranking

        intents = self._process_classifers_output(classifiers_output)

        ranking = []
        if self.strategy == 'average':
            for intent, score in intents.items():
                ranking.append({'name': intent, 'score': score})
        elif self.strategy == 'max':
            for intent, detail in intents.items():
                ranking.append({'name': intent, 'score': detail['score'], 'classifier': detail['classifier']})

        ranking.sort(key=lambda i: i['score'], reverse=True)

        return ranking

    def process(self, message: Message):
        ranking = self.predict(message)

        message.intents_ranking = ranking

        # Check intent threshold
        if (message.intents_ranking[0]['score'] > self.confident_threshold and
                message.intents_ranking[0]['score'] - message.intents_ranking[1]['score'] > self.ambiguity_threshold):
            message.intent = message.intents_ranking[0]['name']

    def get_metadata(self):
        metadata = {
            'name': self.name,
            'type': self.component_type,
            'strategy': self.strategy,
            'classifier_weights': self.weights,
            'classifiers': [c.get_metadata() for c in self.classifiers],
            'confident_threshold': self.confident_threshold,
            'ambiguity_threshold': self.ambiguity_threshold,
        }
        return metadata

    def save(self, path: Text):
        for classifier in self.classifiers:
            classifier.save(path)

    @classmethod
    def load(cls, path: Text, metadata: Dict[Text, Any], **kwargs):
        from fastbot.nlu.registry import load_component

        classifier_weights = metadata.get('classifier_weights', [])
        strategy = metadata.get('strategy', 'max')
        classifiers = []

        for classifier_metadata in metadata.get('classifiers', []):
            classifier_type = classifier_metadata['type']
            classifier = load_component(classifier_type, path, classifier_metadata)
            classifiers.append(classifier)

        ensemble_classifier = cls(classifiers, strategy, classifier_weights, name=metadata['name'])
        ensemble_classifier.confident_threshold = metadata['confident_threshold']
        ensemble_classifier.ambiguity_threshold = metadata['ambiguity_threshold']
        return ensemble_classifier
