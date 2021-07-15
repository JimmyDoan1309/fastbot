from . import BaseSchema
from marshmallow import Schema, fields
from fastbot.models.nlu_data import Sample, NluData


class SampleSchema(BaseSchema):
    __cls_model__ = Sample
    text = fields.String()


class NluDataSchema(BaseSchema):
    __cls_model__ = NluData
    intents = fields.Dict(fields.String(), fields.List(fields.Nested(SampleSchema)))
