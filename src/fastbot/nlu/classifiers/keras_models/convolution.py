from .. import Classifier
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from typing import Text, List, Dict, Any, Union
from sklearn.metrics import accuracy_score, f1_score
import numpy as np

TRAINING = 'training'
INFERENCING = 'inferencing'


class ConvolutionClassifier(Classifier):
    name = 'ConvolutionClassifier'

    def __init__(self, max_sequence_len: int = 30, batch_size: int = 64, epochs: int = 150, **kwargs):
        super().__init__(**kwargs)
        self.max_sequence_len = max_sequence_len
        self.batch_size = batch_size
        self.epochs = epochs
        self.verbose = kwargs.get('verbose', 0)
        self.model = None
        self._model_mode = None

    def _padding(self, sequence: np.ndarray):
        if len(sequence) > self.max_sequence_len:
            return sequence[:self.max_sequence_len, :]
        elif len(sequence) < self.max_sequence_len:
            embed_dims = sequence.shape[-1]
            pad_size = self.max_sequence_len - len(sequence)

            zeros_padding = np.zeros((pad_size, embed_dims))
            return np.concatenate((zeros_padding, sequence))
        return sequence

    def _one_hot(self, intent: Text):
        oh = np.zeros(self.number_of_intent)
        oh[self.intent2idx[intent]] = 1
        return oh

    def _prepared_data(self, data: NluData, create_label_mapping: bool = False):
        if create_label_mapping:
            self._create_label_mapping(data)

        X = []
        y = []
        for intent, samples in data.intents.items():
            for sample in samples:
                X.append(self._padding(sample.nlu_cache.dense_embedding_vector))
                y.append(self._one_hot(intent))

        X = np.asarray(X)
        y = np.asarray(y)

        return X, y

    def train(self, data: NluData):
        try:
            from tensorflow import keras
        except:
            raise ModuleNotFoundError('Tensorflow is soft-required module for training only. Please install it seperately.')

        self._model_mode = TRAINING

        X, y = self._prepared_data(data, True)
        self.model = keras.models.Sequential([
            keras.layers.InputLayer(input_shape=X.shape[1:]),
            keras.layers.Conv1D(filters=64, kernel_size=5,
                                strides=1, padding='same',
                                activation='relu'),
            keras.layers.Conv1D(filters=64, kernel_size=5,
                                strides=1, padding='same',
                                activation='relu'),
            keras.layers.MaxPool1D(),
            keras.layers.Conv1D(filters=128, kernel_size=3,
                                strides=1, padding='same',
                                activation='relu'),
            keras.layers.Conv1D(filters=128, kernel_size=3,
                                strides=1, padding='same',
                                activation='relu'),
            keras.layers.MaxPool1D(),
            keras.layers.Flatten(),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(256),
            keras.layers.Dense(units=self.number_of_intent, activation='softmax')
        ])
        optimizer = keras.optimizers.Adam(learning_rate=0.001)
        self.model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['acc'])

        early_stop = keras.callbacks.EarlyStopping(monitor='loss', min_delta=0.001, patience=10, mode='min', restore_best_weights=True)
        hist = self.model.fit(X, y,
                              batch_size=self.batch_size,
                              epochs=self.epochs,
                              verbose=self.verbose,
                              callbacks=[early_stop])

        hist = hist.history
        print(f'{self.name} finishes training with loss = {hist["loss"][-1]}, acc = {hist["acc"][-1]}')

    def predict_test_data(self, test_data: NluData):
        if self._model_mode == INFERENCING:
            raise Exception('Cannot evaluate when keras model at inference mode')

        X, y_true = self._prepared_data(test_data)
        y_pred = self.model.predict(X)  # pylint: disable=no-member
        y_true = np.argmax(y_true, axis=-1)
        return y_true, y_pred

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
                'y_true': [self.idx2intent[true] for true in y_true]
            }
        }

        return results

    def _tflite_predict(self, inp: np.ndarray):
        inp = np.float32(inp)
        input_detail = self.model.get_input_details()[0]
        output_detail = self.model.get_output_details()[0]
        self.model.allocate_tensors()
        self.model.set_tensor(input_detail['index'], inp)
        self.model.invoke()
        output = self.model.get_tensor(output_detail['index'])
        return output

    def predict(self, message: Message):
        if not message.text:
            return []

        vec = message.nlu_cache.dense_embedding_vector
        vec = self._padding(vec)
        vec = np.expand_dims(vec, axis=0)

        if self._model_mode == TRAINING:
            probs = self.model.predict(vec)[0]  # pylint: disable=no-member
        elif self._model_mode == INFERENCING:
            probs = self._tflite_predict(vec)[0]
        else:
            raise Exception(f'model_mode must be `training` or `inferencing`')

        ranking = []
        for i, prob in enumerate(probs):
            ranking.append({'name': self.idx2intent[i], 'score': prob})
        ranking.sort(key=lambda i: i['score'], reverse=True)

        return ranking

    def process(self, message: Message):
        ranking = self.predict(message)

        if ranking:
            message.nlu_cache.classifiers_output[self.name] = ranking
            message.intents_ranking = ranking

            # Check intent threshold
            if (message.intents_ranking[0]['score'] > self.confident_threshold and
                    message.intents_ranking[0]['score'] - message.intents_ranking[1]['score'] > self.ambiguity_threshold):
                message.intent = message.intents_ranking[0]['name']

    def get_metadata(self):
        metadata = {
            'name': self.name,
            'type': self.component_type,
            'intents': self.intents,
            'max_sequence_len': self.max_sequence_len,
            'confident_threshold': self.confident_threshold,
            'ambiguity_threshold': self.ambiguity_threshold,
        }
        return metadata

    def save(self, path: Text):
        if (self._model_mode != 'training'):
            return

        try:
            import tensorflow as tf
        except:
            raise ModuleNotFoundError('Tensorflow is soft-required module for training keras model. Please install it seperately.')

        # Convert the model.
        converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
        tflite_model = converter.convert()

        # Save the model.
        with open(f'{path}/{self.name}.tflite', 'wb') as fp:
            fp.write(tflite_model)

    @classmethod
    def load(cls, path: Text, metadata: Dict[Text, Any], **kwargs):
        try:
            import tflite_runtime.interpreter as tflite
        except:
            raise ModuleNotFoundError("""
                    tflite_runtime module is soft-required for load keras model for inference. Please install it seperately.
                    Visit `https://www.tensorflow.org/lite/guide/python` for guide on how to install appropriate
                        tflite_runtime package for your OS and python's version. 
                    """)

        classifier = cls()
        classifier.model = tflite.Interpreter(f'{path}/{metadata["name"]}.tflite')
        classifier._update_properties(metadata)
        return classifier

    def _update_properties(self, metadata: Dict[Text, Any]):
        self.name = metadata['name']
        self.intents = metadata['intents']
        self.max_sequence_len = metadata['max_sequence_len']
        self.number_of_intent = len(self.intents)
        self.intent2idx = {intent: idx for idx, intent in enumerate(self.intents)}
        self.idx2intent = {idx: intent for intent, idx in self.intent2idx.items()}
        self._model_mode = INFERENCING
