from .component import BaseComponent
from fastbot.models.nlu_data import NluData, Sample, TRAIN_DATA
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
        self.auto_download = auto_download
        self.entity_dimensions = kwargs.get("entity_dimensions", [])
        self.model = self.load_model()
        if self.all_tasks:
            self.named_entities = True
            self.vectorization = True
            self.tokenization = True
            self.pos_tagging = True
        elif self.pos_tagging:
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
            message.nlu_cache.tokens = [token.text for token in doc]

    def _vectorize(self, doc: spacy.tokens.Doc, message: Union[Message, Sample]):
        if self.vectorization:
            message.nlu_cache.dense_embedding_vector = np.array([token.vector for token in doc])

    def _extract_entities(self, doc: spacy.tokens.Doc, message: Union[Message, Sample]):
        if self.named_entities:
            for ent in doc.ents:
                if ent.label_ in self.entity_dimensions or not self.entity_dimensions:
                    message.entities.append(Entity(
                        ent.label_,
                        ent.start_char,
                        ent.end_char,
                        ent.text,
                        self.component_type))

    def _pos_tagging(self, doc: spacy.tokens.Doc, message: Union[Message, Sample]):
        if self.pos_tagging:
            pos_tag = []
            entity = 'None'
            for token in doc:
                features = {
                    'word': token.text,
                    'pos': token.pos_,
                    'tag': token.tag_,
                    'dep': token.dep_,
                    'like_num': token.like_num,
                    'like_email': token.like_email,
                    'like_url': token.like_url,
                    'lemma': token.lemma_,
                    'start': token.idx,
                    'end': token.idx+len(token),
                    'ner': None
                }
                if (isinstance(message, Sample)):
                    ner, entity = self._parse_custom_ner(message, token.text, entity)
                    features['ner'] = ner
                pos_tag.append(features)
            message.nlu_cache.pos_tag = pos_tag

    def _parse_custom_ner(self,
                          message: Sample,
                          token: Text,
                          prev_entity: Text):
        for e in message.entities:
            if e.extractor != TRAIN_DATA:
                continue
            span = message.text[e.start: e.end]
            if token in span:
                if prev_entity == e.entity:
                    return f'I-{e.entity}', e.entity
                else:
                    return f'B-{e.entity}', e.entity
        return 'O', 'None'

    def train(self, data: NluData):
        for sample in data.all_samples:
            doc = self.model(sample.nlu_cache.processed_text)
            self._tokenize(doc, sample)
            self._vectorize(doc, sample)
            self._extract_entities(doc, sample)
            self._pos_tagging(doc, sample)

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
            "auto_download": self.auto_download,
            "entity_dimensions": self.entity_dimensions,
        }

    def save(self, path: Text):
        pass

    @classmethod
    def load(cls, path: Text, metadata: Dict[Text, Any], **kwargs):
        return cls(**metadata)
