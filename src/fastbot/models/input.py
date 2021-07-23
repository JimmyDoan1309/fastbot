from typing import List, Text, Dict, Any, Optional, Union, Callable
from fastbot.utils.common import import_from_path


class EscapeIntentAction:
    def __init__(self, intent: Text, next_node: Text):
        self.intent = intent
        self.next_node = next_node


class InputMapping:
    """
    Attributes:
        - itype: input mapping type [entity, intent or text]
        - values: applied for itype = [entity, intent], what entities/intents will map to this input slot
        - always_ask: always explicitly ask for input instead infer from current message at input mapping level
        - multiple: applied for itype = entity. Allow for multiple instances of a entity
        - drop: applied for itype = entity. Whether or not to removed entity instances from cache,
                so future input slots that also required this entity type cannot be refer to the same
                instance

    """

    def __init__(self, itype: Text,
                 values: Union[List[Text], Text] = None,
                 always_ask: bool = False,
                 multiple: bool = True,
                 drop: bool = True):
        if (itype == 'entity' and not values):
            raise Exception('A list of entity must be provided for `entity` mapping')
        self.itype = itype
        self.values = values
        self.always_ask = always_ask
        self.multiple = multiple
        self.drop = drop
        if itype == 'text':
            self.always_ask = True


class InputConfig:
    """
    Attributes:
        - name: Name of the input slot
        - maps: List[InputMapping] config. Because a slot can be filled by multiple ways (entity, intent, text)
        - prompts: What to says when ask for this input slot
        - reprompts: What to says when re-ask for this input slot
        - default: the default value when users do not provide the asked field (or field cannot be extracted)
        - default_delay_step: how many step to prompts before applied default value
        - always_ask: always explicitly ask for input instead infer from current message
        - optional: is field optional
        - allow_override: list of InputMapping itype allow to get override during filing the form, default to ['entity'] only
        - validator: import path to function that will run when asked field is extracted successfully.
                     Usually use for extra validation step. 
                     Ex: Extract entity using RegexExtractor but need to verify the result with some external database

                     Arguments:
                        - itype: input mapping type
                        - value: the value of the input slot, can be either a list or a single value depend on mapping.multiple
                        - context: ContextManager, allow you to do almost anything

                    Returns: value (return None if the validation fail)

                     def validation(itype:str, value:Any, context:ContextManager):
                         return value
    """

    def __init__(self, name: Text,
                 maps: Union[List[Dict], List[InputMapping]],
                 prompts: List[Text] = [],
                 reprompts: Optional[List[Text]] = None,
                 default: Optional[Any] = None,
                 default_delay_step: Optional[int] = 0,
                 always_ask: Optional[bool] = False,
                 optional: Optional[bool] = False,
                 allow_override: List[Text] = ['entity'],
                 validator: Optional[Union[Text, Callable]] = None):
        if isinstance(maps[0], Dict):
            from fastbot.schema.input import InputMappingSchema
            maps = InputMappingSchema(many=True).load(maps)

        self.name = name
        self.maps = maps
        self.prompts = prompts
        self.reprompts = reprompts
        self.default = default
        self.default_delay_step = default_delay_step
        self.always_ask = always_ask
        self.optional = optional
        self.allow_override = allow_override
        self.validator = build_validator(validator) if validator != None else None


def build_validator(validator: Union[Text, Callable]):
    if isinstance(validator, Text):
        return import_from_path(validator)
    return validator
