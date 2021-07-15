from .base import Extractor
from fastbot.models import Message, Entity
from fastbot.models.entity import ListEntityConfig
from typing import Text, List, Dict, Any, Union
import re


class ListExtractor(Extractor):
    """
    Extract entities from messages using a list of values + their synonyms
    """

    name = 'ListExtractor'

    def __init__(self, entity_config: Union[Dict, ListEntityConfig], **kwargs):
        super().__init__(**kwargs)

        if isinstance(entity_config, Dict):
            from fastbot.schema.entity import ListEntityConfigSchema
            entity_config = ListEntityConfigSchema().load(entity_config)

        self.entity_name = entity_config.name
        self.list = entity_config.values
        self.case_sensitive = entity_config.case_sensitive

    def convert_to_entity(self, value: Any, text: Text, start: int, end: int):
        return Entity(self.entity_name, value, start, end, self.name, text=text)

    def process(self, message: Message):
        text = message.text

        entities = []
        for item in self.list:
            search_terms = [item.name] + item.synonyms

            if not self.case_sensitive:
                search_terms = list(set([term.lower() for term in search_terms]))
                text = text.lower()

            search_terms.sort(key=len, reverse=True)
            overlaps = []
            for term in search_terms:
                for match in re.finditer(fr'\b{term}\b', text):
                    start_index = match.start(0)
                    end_index = match.end(0)
                    # if a term is a substring of one of the previous terms, ignore
                    if not self._is_overlaps((start_index, end_index), overlaps):
                        item_value = item.code if item.code else item.name
                        entities.append(self.convert_to_entity(
                            item_value,
                            term,
                            start_index,
                            end_index,
                        ))
                        overlaps.append((start_index, end_index))
        return entities

    @staticmethod
    def _is_overlaps(current_term_idx, prev_terms_idx):
        for prev_term_idx in prev_terms_idx:
            if current_term_idx[0] <= prev_term_idx[1] and prev_term_idx[0] <= current_term_idx[1]:
                return True
        return False
