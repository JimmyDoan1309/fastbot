from . import Ner
from fastbot.schema.nlu_data import NluData
from fastbot.models.message import Message, Entity
from typing import Text, List, Dict, Any
from spacy.training.example import Example
from spacy.util import minibatch
import spacy
import numpy as np
import logging
import random

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class SpacyNER(Ner):
    name = 'SpacyNER'

    def __init__(self, spacy_entities: List[Text] = [], language_model: Text = "xx_ent_wiki_sm", batch_size=32, epochs=30, auto_download=False, train_components=['ner'], **kwargs):
        super().__init__(**kwargs)
        self.language_model = language_model
        self.batch_size = batch_size
        self.epochs = epochs
        self.auto_download = auto_download
        self.custom_entities = []
        self.spacy_entites = spacy_entities
        self.verbose = kwargs.get('verbose', 0)
        self.disable = kwargs.get('disable_components', ["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"])
        self.model = None
        self.train_components = train_components
        self.freeze_components = [component for component in self.model.pipe_names if component not in train_components]

    def load_model(self):
        try:
            self.model = spacy.load(self.language_model, disable=self.disable)
        except Exception as e:
            log.warning(f'{language_model} does not exist!')
            if self.auto_download:
                log.info(f'Auto download {language_model}...')
                import subprocess
                download = subprocess.Popen(['python', '-m', 'spacy', 'download', language_model])
                download.wait()
                self.model = spacy.load(language_model, disable=self.disable)
            else:
                raise e

    def prepare_data(self, data: NluData):
        entities_data = [sample for sample in data.all_samples if sample.entities != []]

        entities = set()
        for sample in entities_data:
            for entity in sample.entities:
                entities.add(entity.entity)

        self.custom_entities = list(entities)

        examples = []
        for sample in entities_data:
            doc = self.model.make_doc(sample.full_text)
            example = Example.from_dict(doc, sample.spacy_format)
            examples.append(example)
        return examples

    def train(self, data: NluData):
        self.load_model()
        examples = self.prepare_data(data)
        # If no custom entities found, skip training
        if not examples:
            if self.verbose > 0:
                log.info("No custom entities")
            return

        if (self.model.has_pipe('ner')):
            ner = self.model.get_pipe('ner')
            optimizer = self.model.resume_training()
        else:
            ner = self.model.add_pipe('ner')
            optimizer = self.model.create_optimizer()

        for entity in self.custom_entities:
            ner.add_label(entity)

        with self.model.disable_pipes(*self.freeze_components):
            for i in range(self.epochs):
                random.shuffle(examples)
                batches = minibatch(examples, size=self.batch_size)
                losses = {}
                for batch in batches:
                    self.model.update(batch, sgd=optimizer, drop=0.35, losses=losses)
                    if self.verbose > 0:
                        log.info(losses)

    def evaluate(self, test_data: NluData):
        pass

    def process(self, message: Message):
        doc = self.model(message.text)
        filters = [*self.custom_entities, *self.spacy_entites]
        for entity in doc.ents:
            if entity.label_ in filters:
                message.entities.append(Entity(
                    entity.label_,
                    entity.text,
                    entity.start_char,
                    entity.end_char,
                    self.component_type))

    def save()
