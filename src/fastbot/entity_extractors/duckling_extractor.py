from .base import Extractor
from .constants import *
from fastbot.models import Message, Entity
from typing import Text, List, Dict, Any, Optional
from dateutil.parser import parse as dateparser
from urllib import parse
import requests
import json
import logging


log = logging.getLogger(__name__)


class DucklingExtractor(Extractor):
    """
    Using Duckling to extract entities from a string.
    This Duckling extractor apply some post processing to make the result look nicer

    Change dimension name
        quantity        -> weight
        distance        -> length
        time            -> time | date | datetime | datetime_interval
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
                # break duckling `time` -> time, date, datetime, datetime_interval
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
        except Exception as e:
            log.error(e)
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

    def _convert_datetime(self, datetime_string:Text, grain: Text):
        if not datetime_string:
            return None, None, None
        date = datetime_string.split('T')[0]
        time = None
        if grain in ['hour', 'minute']:
            time = datetime_string.split('T')[1]
        datetime = {'date': date, 'time': time}
        return datetime, date, time
        

    def convert_to_entity(self, value: Any, entity: Text, start: int, end: int, unit: Text = None):
        return Entity(entity, start, end, value, self.name, unit)

    def _extract_values_to_entities(self, match):
        entities = []
        entity_type, value_type, value, unit, grain = self._extract_value(match)
        if value_type == 'interval':
            if entity_type == 'time':
                from_date = self._convert_datetime(value.get('from'), grain)[0]
                to_date = self._convert_datetime(value.get('to'), grain)[0]
                entities.append(self.convert_to_entity({'from': from_date, 'to': to_date}, 'datetime_interval', match['start'], match['end'], unit=grain))
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
                datetime, date, time = self._convert_datetime(value, grain)
                entities.append(self.convert_to_entity(datetime, 'datetime', match['start'], match['end'], unit=grain))
                entities.append(self.convert_to_entity(date, 'date', match['start'], match['end'], unit=grain))
                if time:
                    entities.append(self.convert_to_entity(time, 'time', match['start'], match['end'], unit=grain))
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
            grain = match['value'].get('from', {}).get('grain')
            unit = t1 if t1 else t2
            value = {
                'to': to_value,
                'from': from_value,
            }
        else:
            unit = match['value'].get('unit')
            value = match['value']['value']
            grain = match['value'].get('grain')
        return entity_type, value_type, value, unit, grain

    def process(self, message: Message):
        text = message.text
        timezone = message.config.get('timezone')
        if not timezone:
            timezone = self.default_timezone
        matches = self._parse(text, timezone)
        entities = self._convert_duckling_format(matches)
        entities = self._remove_irrelevant_entities(entities)

        return entities
