from . import BaseSchema
from marshmallow import Schema, fields, validates_schema, validates, ValidationError
from fastbot.models.nlu_data import Sample, NluData
from fastbot.models.entity import Entity
from fastbot.utils.common import parse_entities_from_text
from marshmallow import post_load


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
    text = fields.String(required=True)
    entities = fields.List(fields.Nested(EntitySchema), default=[])

    @post_load
    def __convert__(self, data, **kwargs):
        text = data.get('text')
        entities = data.get('entities', [])
        text, text_entities = parse_entities_from_text(text)
        if text_entities:
            text_entities = EntitySchema(many=True).load(text_entities)
        entities.extend(text_entities)
        return self.__cls_model__(text, entities)


class NluDataSchema(BaseSchema):
    __cls_model__ = NluData
    intents = fields.Dict(fields.String(), fields.List(fields.Nested(SampleSchema)))
