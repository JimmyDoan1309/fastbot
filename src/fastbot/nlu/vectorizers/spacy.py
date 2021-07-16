from . import Vectorizer
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message
from typing import Text, List, Dict, Any
import spacy
import numpy as np
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class SpacyVectorizer(Vectorizer):
    name = 'SpacyVectorizer'

    def __init__(self, language_model: Text, auto_download=False, **kwargs):
        super().__init__(**kwargs)
        self.language_model = language_model
        self.auto_download = auto_download
        try:
            self.model = spacy.load(language_model)
        except Exception as e:
            log.warning(f'{language_model} does not exist!')
            if self.auto_download:
                log.info(f'Auto download {language_model}...')
                import subprocess
                download = subprocess.Popen(['python', '-m', 'spacy', 'download', language_model])
                download.wait()
                self.model = spacy.load(language_model)
            else:
                raise e

    def train(self, data: NluData):
        for sample in data.all_samples:
            text = sample.nlu_cache.processed_text
            doc = self.model(text)
            embed = np.asarray([token.vector for token in doc])
            sample.nlu_cache.dense_embedding_vector = embed

    def process(self, message: Message):
        doc = self.model(message.nlu_cache.processed_text)
        embed = np.asarray([token.vector for token in doc])
        message.nlu_cache.dense_embedding_vector = embed

    def get_metadata(self):
        return {
            'name': self.name,
            'type': self.component_type,
            'language_model': self.language_model,
            'auto_download': self.auto_download
        }

    def save(self):
        pass

    @classmethod
    def load(cls, metadata: Dict[Text, Any], **kwargs):
        name = metadata.get('name', cls.name)
        language_model = metadata['language_model']
        auto_download = metadata['auto_download']
        return cls(language_model, auto_download, name=name)
