from marshmallow import INCLUDE, Schema, fields, post_load, pre_load, validate
import re


class BaseSchema(Schema):
    __cls_model__ = dict

    class Meta:
        unknown = INCLUDE

    @pre_load
    def __pre_load__(self, data, **kwargs):
        if isinstance(data, self.__cls_model__):
            return data.__dict__
        return data

    @post_load
    def __convert__(self, data, **kwargs):
        return self.__cls_model__(**data)
