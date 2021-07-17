from . import BaseSchema
from marshmallow import Schema, fields, validates_schema, validates, ValidationError
from fastbot.models.nlu_data import Sample, NluData
from fastbot.models.entity import Entity


class EntitySchema(BaseSchema):
    __cls_model__ = Entity
    start = fields.Integer(required=True)
    end = fields.Integer(required=True)
    entity = fields.String(required=True)

    @validates_schema
    def validate(self, data: dict, **kwargs):
        if data['end'] <= data['start']:
            raise ValidationError(f'`end` must be greater than `start`')


class SampleSchema(BaseSchema):
    __cls_model__ = Sample
    text = fields.String()
    entities = fields.List(fields.Nested(EntitySchema), default=[])


class NluDataSchema(BaseSchema):
    __cls_model__ = NluData
    intents = fields.Dict(fields.String(), fields.List(fields.Nested(SampleSchema)))
