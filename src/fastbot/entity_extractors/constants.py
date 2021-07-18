import os

DEFAULT_TZ = 'UTC'
DUCKLING_LOCALE = {
    'en': 'en_US',
    'vi': 'vi_NL',
}

ENTITY_PREFIX = '@'

DUCKLING_ENDPOINT = os.getenv('DUCKLING_ENDPOINT', 'http://localhost:8000')
DEFAULT_TEMP_UNIT = os.getenv('DEFAULT_TEMP_UNIT', 'celsius')

ENTITY_MAPPING = {
    'quantity': 'weight',
    'distance': 'length',
    'amount-of-money': 'currency',
}
REVERSED_ENTITY_MAPPING = {v: k for k, v in ENTITY_MAPPING.items()}


DUCKLING_OTHER_ENTITIES = ['number', 'email', 'url', 'ordinal', 'currency']
DUCKLING_MEASURE_ENTITIES = ['weight', 'volume', 'duration', 'temperature', 'length']
DUCKLING_TIME_ENTITIES = ['time', 'date', 'datetime', 'datetime_interval']
DUCKLING_ENTITIES = DUCKLING_TIME_ENTITIES+DUCKLING_MEASURE_ENTITIES+DUCKLING_OTHER_ENTITIES


SPECIAL_ENTITIES = ['list', 'regex', 'composite']
