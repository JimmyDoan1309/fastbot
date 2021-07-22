from . import BaseSchema
from marshmallow import fields, validates_schema, validates, ValidationError
from fastbot.models.policy_data import PolicyData, Story, Step
from typing import List


class StepSchema(BaseSchema):
    __cls_model__ = Step

    intent = fields.String(required=False)
    action = fields.String(required=False)

    @validates_schema
    def validate(self, data: dict, **kwargs):
        if data.get('intent') and data.get('action'):
            raise ValidationError('Each step must has one of two field `intent` or `action` (but not both)')
        if data.get('intent') is None and data.get('action') is None:
            raise ValidationError('Each step must has one of two field `intent` or `action`')


class StorySchema(BaseSchema):
    __cls_model__ = Story

    name = fields.String(required=False)
    steps = fields.List(fields.Nested(StepSchema), default=[])

    @validates('steps')
    def validate_steps(self, steps: List[Step]):
        if len(steps) == 0:
            raise ValidationError('Number of steps in a story must greater than 0')
        if not steps[-1].action:
            raise ValidationError('Last step of a story must be an action')


class PolicyDataSchema(BaseSchema):
    __cls_model__ = PolicyData
    stories = fields.List(fields.Nested(StorySchema), default=[])
