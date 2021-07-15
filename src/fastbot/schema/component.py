from marshmallow import Schema, fields, validates, ValidationError
from fastbot.models.component import ComponentConfig
from . import BaseSchema


class ComponentConfigSchema(BaseSchema):
    __cls_model__ = ComponentConfig
    name = fields.String(required=True)
    type = fields.String(required=True)
    arguements = fields.Raw(default={})
