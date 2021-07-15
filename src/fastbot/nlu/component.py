from typing import Text, Dict, Any
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
import pickle


class BaseComponent:
    name = "BaseComponent"

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', self.name)
        self.config = kwargs

    def train(self, data: NluData):
        raise NotImplementedError('Subclass must implement this')

    def process(self, message: Message):
        raise NotImplementedError('Subclass must implement this')
    
    def evaluate(self, test_data: NluData):
        """
        Evaluate test data. For components that doesn't have internal states
        change (ex: classifier model, vectorizer) during the training phase.
        Evaluating is the same as training. Overide this method for
        component that has internal states changes
        """
        self.train(test_data)

    def get_metadata(self):
        """
        Get component metadata for persitance. By default return 
        component name only. Override this method for custom behavior
        """
        return {'name': self.name, 'type': self.component_type}

    def save(self, path: Text):
        """
        Persit a component object, default using pickle.
        Override this method for custom behavior
        """
        with open(f'{path}/{self.name}.pkl', 'wb') as fp:
            pickle.dump(self, fp)

    @classmethod
    def load(cls, path: Text, metadata: Dict[Text, Any], **kwargs):
        """
        Load a component object, default using pickle.
        Override this method for custom behavior
        """
        with open(f'{path}/{metadata["name"]}.pkl', 'rb') as fp:
            component = pickle.load(fp)
            return component

    @property
    def component_type(self):
        return self.__class__.__name__
