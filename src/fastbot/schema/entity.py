from . import BaseSchema
from marshmallow import Schema, fields, validates, ValidationError
from fastbot.models.entity import (
    MeasurementEntityConfig,
    ListEntityConfig,
    ListEntityItem,
    RegexEntityConfig,
    CompositeEntityConfig,
    CustomEntityConfig
)
from fastbot.entity_extractors.constants import DUCKLING_MEASURE_ENTITIES


class MeasurementEntityConfigSchema(BaseSchema):
    __cls_model__ = MeasurementEntityConfig
    measure = fields.String(required=True)
    default_unit = fields.String(required=True)

    @validates('measure')
    def validate_measure(self, measure):
        if measure not in DUCKLING_MEASURE_ENTITIES:
            raise ValidationError(f'measure type must be in {DUCKLING_MEASURE_ENTITIES}')


class ListEntityItemSchema(BaseSchema):
    __cls_model__ = ListEntityItem
    name = fields.String(required=True)
    code = fields.String()
    synonyms = fields.List(fields.String(), default=[])


class ListEntityConfigSchema(BaseSchema):
    __cls_model__ = ListEntityConfig
    name = fields.String(required=True)
    values = fields.List(fields.Nested(ListEntityItemSchema), default=[])
    case_sensitive = fields.Bool(default=True)
    fuzzy_match = fields.Bool(default=False)
    fuzzy_match_threshold = fields.Float(default=70.0)
    fuzzy_match_min_search_length = fields.Integer(default=5)


class RegexEntityConfigSchema(BaseSchema):
    __cls_model__ = RegexEntityConfig
    name = fields.String(required=True)
    patterns = fields.List(fields.String())


class CompositeEntityConfigSchema(BaseSchema):
    __cls_model__ = CompositeEntityConfig
    name = fields.String(required=True)
    patterns = fields.List(fields.String())


class CustomEntityConfigSchema(BaseSchema):
    __cls_model__ = CustomEntityConfig
    name = fields.String(required=True)
    extractor = fields.String(required=True)
    arguments = fields.Dict(fields.String(), fields.Raw(), default={})
