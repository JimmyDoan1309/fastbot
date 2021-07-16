from .component import BaseComponent
from fastbot.schema.nlu_data import NluData, Sample
from fastbot.models.message import Message, Entity
from typing import Text, List, Dict, Any, Optional, Union
import spacy
import numpy as np
import logging
import random

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class SpacyPipeline(BaseComponent):
    """
    Load a spacy model and run through its (relevant) Linguistic Features
        - Named Entites
        - Vectorization (Word embedding)
        - Tokenization
        - Pos Tagging
        - Dependency Parsing

    Enable 
    """

    name = 'SpacyPipeline'

    def __init__(
        self,
        language_model: Text = "en_core_web_sm",
        all_tasks: bool = False,
        named_entities: bool = False,
        vectorization: bool = False,
        tokenization: bool = False,
        pos_tagging: bool = False,
        dependency_parse: bool = False,
        auto_download: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.language_model = language_model
        self.all_tasks = all_tasks
        self.named_entities = named_entities
        self.vectorization = vectorization
        self.tokenization = tokenization
        self.pos_tagging = pos_tagging
        self.dependency_parse = dependency_parse
        self.auto_download = auto_download
        self.entity_dimensions = kwargs.get("entity_dimensions", [])
        self.model = self.load_model()
        if self.all_tasks:
            self.named_entities = True
            self.vectorization = True
            self.tokenization = True
            self.pos_tagging = True
            self.dependency_parse = True
        elif self.pos_tagging or self.dependency_parse:
            self.tokenization = True

    def load_model(self):
        try:
            return spacy.load(self.language_model)
        except Exception as e:
            log.warning(f'{self.language_model} does not exist!')
            if self.auto_download:
                log.info(f'Auto download {self.language_model}...')
                import subprocess
                download = subprocess.Popen(['python', '-m', 'spacy', 'download', self.language_model])
                download.wait()
                return spacy.load(self.language_model)
            else:
                raise e

    def _tokenize(self, doc: spacy.tokens.Doc, message: Union[Message, Sample]):
        if self.tokenization:
            message.nlu_cache.tokenized_text = [token.text for token in doc]

    def _vectorize(self, doc: spacy.tokens.Doc, message: Union[Message, Sample]):
        if self.vectorization:
            message.nlu_cache.dense_embedding_vector = np.array([token.vector for token in doc])

    def _extract_entities(self, doc: spacy.tokens.Doc, message: Union[Message, Sample]):
        if self.named_entities:
            for ent in doc.ents:
                if ent.label_ in self.entity_dimensions or not self.entity_dimensions:
                    message.entities.append(Entity(
                        ent.label_,
                        ent.text,
                        ent.start_char,
                        ent.end_char,
                        self.component_type))

    def _pos_tagging(self, doc: spacy.tokens.Doc, message: Union[Message, Sample]):
        if self.pos_tagging:
            message.nlu_cache.pos_tag = {token.text: token.pos_ for token in doc if token.pos_}

    def train(self, data: NluData):
        for sample in data.all_samples:
            doc = self.model(sample.nlu_cache.processed_text)
            self._tokenize(doc, sample)
            self._vectorize(doc, sample)

    def process(self, message: Message):
        doc = self.model(message.nlu_cache.processed_text)
        self._tokenize(doc, message)
        self._vectorize(doc, message)
        self._extract_entities(doc, message)
        self._pos_tagging(doc, message)

    def get_metadata(self):
        return {
            "name": self.name,
            "type": self.component_type,
            "language_model": self.language_model,
            "all_tasks": self.all_tasks,
            "named_entities": self.named_entities,
            "vectorization": self.vectorization,
            "tokenization": self.tokenization,
            "pos_tagging": self.pos_tagging,
            "dependency_parse": self.dependency_parse,
            "auto_download": self.auto_download,
            "entity_dimensions": self.entity_dimensions,
        }

    def save(self, path: Text):
        pass

    @classmethod
    def load(cls, path: Text, metadata: Dict[Text, Any], **kwargs):
        return cls(**metadata)
