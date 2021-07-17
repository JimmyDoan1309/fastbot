from .base import Extractor
from .constants import ENTITY_PREFIX
from fastbot.models import Message, Entity
from fastbot.models.entity import CompositeEntityConfig
from typing import Any, Dict, List, Text, Union
import itertools
import re


class CompositeEntitiesExtractor(Extractor):
    """
    Composite Entities Extractor group multiple sub-entities into 
    a single entity by using pattern.
    It will remove all the sub-entities from message output after that.
    Ex: car = '@number @color @car_make @car_model ' -> '2018 red toyota camry'
    """

    name = 'CompositeEntitiesExtractor'

    def __init__(self, entity_config: Union[Dict, CompositeEntityConfig], **kwargs):
        super().__init__(**kwargs)

        if isinstance(entity_config, Dict):
            from fastbot.schema.entity import CompositeEntityConfigSchema
            entity_config = CompositeEntityConfigSchema().load(entity_config)

        self.entity_name = entity_config.name
        self.patterns = entity_config.patterns

    def process(self, message: Message):
        return self._find_composite_entities(message.text, message.entities)

    @staticmethod
    def _replace_entity_values(text, entities_perms: List[List[Entity]]):
        """
        Replace entity values with their respective entity name.
        """
        new_texts = []
        index_maps = []
        for entities in entities_perms:
            new_text = ''
            index_map = []
            n_entities = len(entities)
            for i in range(n_entities):
                current_entity = entities[i][1]
                entity_index = entities[i][0]

                if i == 0:
                    new_text += text[: current_entity.start]

                entity_start = len(new_text)
                new_text += ENTITY_PREFIX + current_entity.entity
                index_map.append((entity_index, entity_start, len(new_text)))

                if i == n_entities - 1:
                    new_text += text[current_entity.end:]
                else:
                    next_entity = entities[i + 1][1]
                    new_text += text[current_entity.end: next_entity.start]

            new_texts.append(new_text)
            index_maps.append(index_map)
        return new_texts, index_maps

    def _find_composite_entities(self, text: Text, entities: List[Entity]):
        if not entities:
            return []

        entities = sorted(entities, key=lambda entity: entity.start)
        entities_perms = self._generate_entites_permuations(entities)

        new_texts, index_maps = self._replace_entity_values(
            text, entities_perms
        )

        all_composites = []
        all_used_indices = set()
        for new_text, index_map in zip(new_texts, index_maps):
            processed_composite_entities = []
            used_entity_indices = []
            contained_entity_indices = []
            mapping_dicts = []

            # Sort patterns (longest pattern first) as longer patterns might
            # contain more information
            for pattern in sorted(self.patterns, key=len, reverse=True):
                pattern, mapping_dict = self._seperate_key_pattern(pattern)
                for match in re.finditer(pattern, new_text):
                    contained_in_match = [
                        index
                        for (index, start, end) in index_map
                        if start >= match.start() and end <= match.end()
                    ]
                    # If any entity for this match is already in the list, than
                    # this pattern is a subset of a previous (larger) pattern
                    # and we can ignore it.
                    all_indices = set(
                        itertools.chain.from_iterable(contained_entity_indices)
                    )
                    if all_indices & set(contained_in_match):
                        continue

                    contained_entity_indices.append(contained_in_match)
                    mapping_dicts.append(mapping_dict)

            if contained_entity_indices:
                for contained_in_match, mapping_dict in zip(contained_entity_indices, mapping_dicts):
                    contained_entities = list(
                        sorted(
                            [entities[i] for i in contained_in_match],
                            key=lambda x: x.start,
                        )
                    )
                    contained_entities, start, end = self._format_composite_entities(contained_entities, mapping_dict)
                    processed_composite_entities.append(self.convert_to_entity(contained_entities, start, end))
                used_entity_indices += list(
                    itertools.chain.from_iterable(contained_entity_indices)
                )

            if processed_composite_entities:
                all_composites += processed_composite_entities
                all_used_indices.update(used_entity_indices)

        filtered_entites = [entity for i, entity in enumerate(entities) if i not in list(all_used_indices)]
        return filtered_entites + all_composites

    def convert_to_entity(self, value: Any, start: int, end: int):
        return Entity(self.entity_name, start, end, value, self.name)

    @staticmethod
    def _seperate_key_pattern(pattern: Text):
        notation = fr'{ENTITY_PREFIX}[\w_]+(:[\w_]+)?'
        mapping_dict = {}
        new_pattern = pattern
        for match in re.finditer(notation, pattern):
            match_text = match.group()
            tmp = match_text.split(':')
            if len(tmp) > 1:
                entity = tmp[0]
                key = tmp[1]
            elif len(tmp) == 1:
                entity = tmp[0]
                key = tmp[0][len(ENTITY_PREFIX):]

            new_pattern = new_pattern.replace(match_text, entity, 1)
            if mapping_dict.get(entity):
                mapping_dict[entity].append(key)
            else:
                mapping_dict[entity] = [key]
        return new_pattern, mapping_dict

    @staticmethod
    def _format_composite_entities(entities_list: List[Entity], mapping_dict):
        result = {}
        start = entities_list[0].start
        end = entities_list[-1].end
        cache = {}
        for entity in entities_list:

            if entity.entity in cache:
                cache[entity.entity] += 1
            else:
                cache[entity.entity] = 0

            keys = mapping_dict[ENTITY_PREFIX+entity.entity]
            key = keys[cache[entity.entity]]

            # If a key appear twice
            # Mmainly because the user doesn't assign an unique
            # key for each entity appearance in the pattern)
            if result.get(key):
                result[key+'_'+str(cache[entity.entity])] = entity.value
            else:
                result[key] = entity.value

        return result, start, end

    @staticmethod
    def _isoverlap(e, other):
        if not other:
            return False
        if e.start <= other.end and other.start <= e.end:
            return True
        return False

    @staticmethod
    def _filter_perms(perms):
        new_perms = []
        for i, perm in enumerate(perms):
            flag = True
            for other in perms[:i]+perms[i+1:]:
                if all(item in other for item in perm):
                    flag = False
            if flag == True:
                new_perms.append(perm)
        return new_perms

    @classmethod
    def _generate_entites_permuations(cls, entities):
        """
        Because entities can overlapping with each other in position
        while Composite Extractor's depended on entities' position to match pattern
        This function generate all the possible non-overlapping entities permuation
        So that the composite entity extractor can try them all
        """
        perms = [[]]
        loop = 1
        perm_index = 0
        n_perm = 0
        n_entities = len(entities)
        cache = {}
        while loop:
            tmp = perms[perm_index]
            signature = str(tmp)
            if cache.get(signature):
                loop -= 1
                continue

            i = tmp[-1][0] if len(tmp) > 0 else 0
            if i > n_entities-1:
                loop -= 1
                continue

            for e in entities[i:]:
                if len(tmp) == 0:
                    last_e = None
                else:
                    last_e = tmp[-1][1]
                if not cls._isoverlap(e, last_e):
                    tmp.append((i, e))
                else:
                    new_perm = tmp[:-1]+[(i, e)]
                    if new_perm not in perms:
                        loop += 1
                        n_perm += 1
                        perms.append(new_perm)
                i += 1

            loop -= 1
            perm_index += 1

            signature = str(tmp)
            cache[signature] = True

        perms = cls._filter_perms(perms)
        return perms
