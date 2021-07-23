from . import BaseSchema
from marshmallow import Schema, fields, validates, ValidationError
from fastbot.models.input import InputMapping, InputConfig, EscapeIntentAction
from typing import Text, List


class EscapeIntentActionSchema(BaseSchema):
    __cls_model__ = EscapeIntentAction
    intent = fields.String(required=True)
    next_node = fields.String(required=True)


class InputMappingSchema(BaseSchema):
    __cls_model__ = InputMapping
    itype = fields.String(required=True)
    values = fields.Raw()
    always_ask = fields.Boolean(default=False)
    multiple = fields.Boolean(default=True)
    drop = fields.Boolean(default=True)

    @validates('itype')
    def validate_itype(self, itype):
        if itype not in ['text', 'entity', 'intent']:
            raise ValidationError('itype must be `text` or `intent` or `entity`')


class InputConfigSchema(BaseSchema):
    __cls_model__ = InputConfig
    name = fields.String(required=True)
    maps = fields.List(fields.Nested(InputMappingSchema), required=True)
    prompts = fields.List(fields.String())
    reprompts = fields.List(fields.String())
    default = fields.Raw()
    default_delay_step = fields.Integer(default=0)
    always_ask = fields.Boolean(default=False)
    optional = fields.Boolean(default=False)
    validator = fields.String()
    allow_override = fields.List(fields.String(), default=['entity'])
