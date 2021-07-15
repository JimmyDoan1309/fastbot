from .base import Extractor
from .constants import *
from fastbot.models import Message, Entity
from typing import Text, List, Dict, Any, Optional
from dateutil.parser import parse as dateparser
from urllib import parse
import requests
import json


class DucklingExtractor(Extractor):
    """
    Using Duckling to extract entities from a string.
    This Duckling extractor apply some post processing to make the result look nicer

    Change dimension name
        quantity        -> weight
        distance        -> length
        time            -> time | date | datetime | date_period
        amount-of-money -> currency
    """

    name = 'DucklingExtractor'

    def __init__(self,
                 dimensions: Optional[List[Text]] = None,
                 endpoint: Optional[Text] = DUCKLING_ENDPOINT,
                 language: Text = 'en',
                 **kwargs):
        super().__init__(**kwargs)
        self.locale = DUCKLING_LOCALE.get(language, f'{language}_NL')
        self.dimensions = dimensions
        self.endpoint = endpoint+'/parse'
        self.default_timezone = kwargs.get('timezone', DEFAULT_TZ)
        self.default_temp_unit = kwargs.get('default_temp_unit', DEFAULT_TEMP_UNIT)

    def _payload(self, text: Text, timezone: Text):
        def _duckling_dimension():
            temp_dims = []
            for dim in self.dimensions:
                # break duckling `time` -> time, date, datetime, date_period
                if dim in DUCKLING_TIME_ENTITIES:
                    temp_dims.append('time')
                else:
                    temp_dims.append(REVERSED_ENTITY_MAPPING.get(dim, dim))
            temp_dims = list(set(temp_dims))
            return parse.quote(json.dumps(temp_dims))

        def _preprocess_text(text):
            return parse.quote(text)

        # query strings can't have unicode characters and white spaces,
        # convert them all to ASCII
        payload = {
            'locale': self.locale,
            'text': _preprocess_text(text),
            'dims': _duckling_dimension(),
            'tz': timezone,
        }
        querystring = ''
        for key, value in payload.items():
            querystring += f'{key}={value}&'
        return querystring[:-1]  # remove the last '&'

    def _parse(self, text: Text, timezone: Text):
        payload = self._payload(text, timezone)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        try:
            resp = requests.post(self.endpoint, data=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return []

    def _remove_irrelevant_entities(self, entities: List[Dict[Text, Any]]):
        cleaned_entities = []
        for entity in entities:
            if entity.entity in self.dimensions:
                cleaned_entities.append(entity)
        return cleaned_entities

    def _convert_duckling_format(self, matches: List[Dict[Text, Any]]):
        extracted = []
        for match in matches:
            extracted.extend(self._extract_values_to_entities(match))
        return extracted

    def convert_to_entity(self, value: Any, entity: Text, start: int, end: int, unit: Text = None):
        return Entity(entity, value, start, end, self.name, unit)

    def _extract_values_to_entities(self, match):
        entities = []
        entity_type, value_type, value, unit = self._extract_value(match)
        if value_type == 'interval':
            if entity_type == 'time':
                entities.append(self.convert_to_entity(value, 'date_period', match['start'], match['end']))
            else:
                if unit == 'degree':
                    # change temperature to default unit
                    entities.append(self.convert_to_entity(value, entity_type, match['start'], match['end'], unit=self.default_temp_unit))

                # duckling classify 'cup' as quantity/weight but usually 'cup' use for volume
                elif unit == 'cup':
                    entities.append(self.convert_to_entity(value, 'volume', match['start'], match['end'], unit=unit))

                else:
                    entities.append(self.convert_to_entity(value, entity_type, match['start'], match['end'], unit=unit))
        else:
            if entity_type == 'time':
                datetime = dateparser(value)
                date = datetime.date()
                time = datetime.time()
                entities.append(self.convert_to_entity(datetime.isoformat(), 'datetime', match['start'], match['end']))
                entities.append(self.convert_to_entity(str(date), 'date', match['start'], match['end']))
                entities.append(self.convert_to_entity(str(time), 'time', match['start'], match['end']))
            else:
                if unit == 'degree':
                    # change temperature to default unit
                    entities.append(self.convert_to_entity(value, entity_type, match['start'], match['end'], unit=self.default_temp_unit))

                # duckling classify 'cup' as quantity/weight but usually 'cup' use for volume
                elif unit == 'cup':
                    entities.append(self.convert_to_entity(value, 'volume', match['start'], match['end'], unit=unit))

                else:
                    entities.append(self.convert_to_entity(value, entity_type, match['start'], match['end'], unit=unit))
        return entities

    def _extract_value(self, match: Dict[Text, Any]):
        entity_type = ENTITY_MAPPING.get(match['dim'], match['dim'])
        value_type = match['value'].get('type')
        if value_type == 'interval':
            from_value = match['value'].get('from', {}).get('value')
            to_value = match['value'].get('to', {}).get('value')
            t1 = match['value'].get('to', {}).get('unit')
            t2 = match['value'].get('from', {}).get('unit')
            unit = t1 if t1 else t2
            value = {
                'to': to_value,
                'from': from_value,
            }
        else:
            unit = match['value'].get('unit')
            value = match['value']['value']
        return entity_type, value_type, value, unit

    def process(self, message: Message):
        text = message.text
        timezone = message.config.get('timezone')
        if not timezone:
            timezone = self.default_timezone
        matches = self._parse(text, timezone)
        entities = self._convert_duckling_format(matches)
        entities = self._remove_irrelevant_entities(entities)

        return entities
