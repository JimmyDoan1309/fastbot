from .base import Extractor
from fastbot.models import Message, Entity
from fastbot.models.entity import ListEntityConfig
from typing import Text, List, Dict, Any, Union
from rapidfuzz import fuzz
import regex as re


FUZZY_FACTOR = 0.17
TERM_LENGTH_WEIGHT = 1.2


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
        self.fuzzy_match = entity_config.fuzzy_match
        self.fuzzy_match_threshold = entity_config.fuzzy_match_threshold
        self.fuzzy_match_min_search_length = entity_config.fuzzy_match_min_search_length

    def convert_to_entity(self, value: Any, text: Text, start: int, end: int, confidence: float) -> Entity:
        return Entity(self.entity_name, start, end, value, self.name, text=text, confidence=confidence)

    def process(self, message: Message) -> List[Entity]:
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
                pattern = fr'\b{term}\b'
                if self.fuzzy_match and len(term) >= self.fuzzy_match_min_search_length:
                    err = round(FUZZY_FACTOR*(len(text)**TERM_LENGTH_WEIGHT))
                    pattern = r'\b(%s){e<=%i}\b' % (term, err)

                for match in re.finditer(pattern, text):
                    start_index = match.start(0)
                    end_index = match.end(0)

                    confidence = 1.0
                    if self.fuzzy_match:
                        confidence = fuzz.partial_ratio(match.group(), term, score_cutoff=self.fuzzy_match_threshold)
                        if confidence == 0:
                            continue

                    # if a term is a substring of one of the previous terms, ignore
                    if not self._is_overlaps((start_index, end_index), overlaps):
                        item_value = item.code if item.code else item.name
                        entity = self.convert_to_entity(item_value, match.group(), start_index, end_index, confidence)
                        entities.append(entity)
                        overlaps.append((start_index, end_index))
        return entities

    @staticmethod
    def _is_overlaps(current_term_idx, prev_terms_idx) -> bool:
        for prev_term_idx in prev_terms_idx:
            if current_term_idx[0] <= prev_term_idx[1] and prev_term_idx[0] <= current_term_idx[1]:
                return True
        return False
