from . import ActionPolicy
from .constants import FALLBACK, UNKOWN
from .policy_result import PolicyResult
from fastbot.dialog.policies.sklearn import SklearnPolicy
from fastbot.dialog.context import ContextManager
from fastbot.models import PolicyData, Step, Message
from typing import List, Text, Tuple, Dict, Any
import numpy as np
import json
import os
import shutil


TRAINING = 'training'
INFERENCING = 'inferencing'


class KerasPolicy(ActionPolicy):
    def __init__(self, max_history: int = 10, batch_size: int = 64, epochs: int = 150, **kwargs):
        super().__init__(**kwargs)
        self.max_history = max_history
        self.batch_size = batch_size
        self.epochs = epochs
        self.verbose = kwargs.get('verbose', 0)
        self.model = None
        self._model_mode = None

    def _padding(self, history: List[int]):
        if len(history) < self.max_history:
            pad_width = (self.max_history-len(history), 0)
            return np.pad(history, pad_width, 'constant', constant_values=0)
        return np.asarray(history[-self.max_history:])

    def _preprocess_data(self, data: PolicyData) -> Tuple[np.ndarray]:
        self.state2idx = {state: i for i, state in enumerate(data.states, start=1)}
        self.action2idx = {action: i for i, action in enumerate(data.actions)}
        self.idx2action = {i: action for action, i in self.action2idx.items()}

        X = []
        y = []
        for story in data.stories:
            history = [self.state2idx[step.hash] for step in story.steps[:-1]]
            history = self._padding(history)
            action = self.action2idx[story.steps[-1].action]

            X.append(history)
            y.append(action)

        X = np.asarray(X)
        y = np.asarray(y)

        return X, y

    def _history_from_context(self, context: ContextManager) -> np.ndarray:
        unk_intent = self.state2idx[f'intent__{UNKOWN}']
        unk_action = self.state2idx[f'action__{FALLBACK}']

        history = context.get_history()
        steps = []
        for step in history:
            if step.action:
                steps.append(self.state2idx.get(step.hash, unk_action))
            else:
                steps.append(self.state2idx.get(step.hash, unk_intent))
        steps = self._padding(steps)
        steps = steps.reshape((1, -1))
        return steps

    def build_model(self, data: PolicyData, X: np.ndarray, y: np.ndarray):
        try:
            from tensorflow import keras
        except:
            raise ModuleNotFoundError('Tensorflow is soft-required module for training only. Please install it seperately.')
        model = keras.models.Sequential([
            keras.layers.Embedding(len(data.states)+1, 64, input_length=self.max_history),
            keras.layers.LSTM(units=128, activation='relu'),
            keras.layers.Dense(units=len(data.actions), activation='softmax')
        ])
        model.compile(optimizer='adam', loss=keras.losses.sparse_categorical_crossentropy, metrics=['acc'])
        return model

    def train(self, data: PolicyData) -> None:

        X, y = self._preprocess_data(data)

        self._model_mode = TRAINING
        self.model = self.build_model(data, X, y)

        hist = self.model.fit(X, y,
                              batch_size=self.batch_size,
                              epochs=self.epochs,
                              verbose=self.verbose)
        hist = hist.history
        print(f'{self.name} finishes training with loss = {hist["loss"][-1]}, acc = {hist["acc"][-1]}')

    def _actions_ranking(self, probs: np.ndarray) -> PolicyResult:
        actions = []
        action = None
        for i, prob in enumerate(probs):
            actions.append({
                'name': self.idx2action[i],
                'score': prob
            })
        actions.sort(key=lambda a: a['score'], reverse=True)
        if (actions[0]['score'] >= self.confident_threshold) and (actions[0]['score']-actions[1]['score'] > self.ambiguity_threshold):
            action = actions[0]['name']
        return PolicyResult(action, actions)

    def tflite_predict(self, x: np.ndarray):
        x = np.float32(x)
        input_detail = self.model.get_input_details()[0]
        output_detail = self.model.get_output_details()[0]
        self.model.allocate_tensors()
        self.model.set_tensor(input_detail['index'], x)
        self.model.invoke()
        output = self.model.get_tensor(output_detail['index'])
        return output

    def process(self, message: Message, context: ContextManager) -> PolicyResult:
        vec = self._history_from_context(context)

        if self._model_mode == TRAINING:
            probs = self.model.predict(vec)[0]  # pylint: disable=no-member
        elif self._model_mode == INFERENCING:
            probs = self.tflite_predict(vec)[0]
        else:
            raise Exception(f'model_mode must be `training` or `inferencing`')

        result = self._actions_ranking(probs)
        return result

    def save(self, path: Text):
        if (self._model_mode != TRAINING):
            return

        try:
            import tensorflow as tf
        except:
            raise ModuleNotFoundError('Tensorflow is soft-required module for training keras model. Please install it seperately.')

        path = os.path.abspath(path)
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)

        metadata = {
            'confident_threshold': self.confident_threshold,
            'ambiguity_threshold': self.ambiguity_threshold,
            'priority': self.priority,
            'state2idx': self.state2idx,
            'action2idx': self.action2idx,
            'max_history': self.max_history,
        }

        with open(f'{path}/metadata.json', 'w+') as fp:
            json.dump(metadata, fp)

        # Save model as tflite
        converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
        tflite_model = converter.convert()
        with open(f'{path}/{self.name}.tflite', 'wb') as fp:
            fp.write(tflite_model)

    @classmethod
    def load(cls, path: Text):
        try:
            import tflite_runtime.interpreter as tflite
        except:
            raise ModuleNotFoundError("""
            tflite_runtime module is soft-required for load keras model for inference. Please install it seperately.
            Visit `https://www.tensorflow.org/lite/guide/python` for guide on how to install appropriate
                tflite_runtime package for your OS and python's version. 
                    """)

        with open(f'{path}/metadata.json', 'r') as fp:
            metadata = json.load(fp)

        component = cls()
        component.confident_threshold = metadata['confident_threshold']
        component.ambiguity_threshold = metadata['ambiguity_threshold']
        component.priority = metadata['priority']
        component.state2idx = metadata['state2idx']
        component.action2idx = metadata['action2idx']
        component.idx2action = {idx: action for action, idx in component.action2idx.items()}
        component.max_history = metadata['max_history']
        component.model = tflite.Interpreter(f'{path}/{cls.__name__}.tflite')
        component._model_mode = INFERENCING

        return component
