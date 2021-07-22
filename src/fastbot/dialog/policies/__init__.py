from .constants import DIALOG_CONFIDENT_THRESHOLD, DIALOG_AMBIGUITY_THRESHOLD
from .policy_result import PolicyResult
from fastbot.models import Message, PolicyData
from fastbot.dialog.context import ContextManager
from typing import Text, Dict, Any
import pickle
import os
import shutil


class ActionPolicy:
    def __init__(self, **kwargs):
        self.confident_threshold = kwargs.get('confident_threshold', DIALOG_CONFIDENT_THRESHOLD)
        self.ambiguity_threshold = kwargs.get('ambiguity_threshold', DIALOG_AMBIGUITY_THRESHOLD)
        self.priority = kwargs.get('priority', 0)

    def train(self, data: PolicyData) -> None:
        raise NotImplementedError("Subclass must implement this")

    def process(self, message: Message, context: ContextManager) -> PolicyResult:
        raise NotImplementedError('Subclass must implement this')

    @property
    def name(self):
        return self.__class__.__name__

    def save(self, path: Text) -> None:
        path = os.path.abspath(path)
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)

        """
        Persit a component object, default using pickle.
        Override this method for custom behavior
        """
        with open(f'{path}/{self.name}.pkl', 'wb') as fp:
            pickle.dump(self, fp)

    @classmethod
    def load(cls, path: Text, **kwargs) -> 'ActionPolicy':
        """
        Load a component object, default using pickle.
        Override this method for custom behavior
        """
        with open(f'{path}/{cls.__name__}.pkl', 'rb') as fp:
            component = pickle.load(fp)
            return component
