from .base import BaseNode
from .status import NodeStatus, NodeResult
from fastbot.dialog.context import ContextManager
from fastbot.models.input import InputConfig, InputMapping, EscapeIntentAction
from fastbot.models.message import Message
from fastbot.models.response import Response
from fastbot.schema.input import InputConfigSchema, EscapeIntentActionSchema
from fastbot.entity_extractors import ExtractorPipeline
from fastbot.entity_extractors.constants import DUCKLING_TIME_ENTITIES
from typing import Text, List, Dict, Any, Union, Optional, Callable
import random


class ITYPE():
    TEXT = 'text'
    INTENT = 'intent'
    ENTITY = 'entity'


OVERRIDE_INPUT_FUNCTION = 'when_input_overrided'
COLLECTED_INPUTS = 'collected_inputs'
CURRENT_MISSING_INPUT = 'current_missing_input'
STEP_COUNT = 'step_count'


class InputsCollector(BaseNode):
    def __init__(self,
                 name: Text,
                 inputs: Union[List[Dict], List[InputConfig]],
                 entity_extractors: Optional[ExtractorPipeline] = None,
                 escape_intent_action: Union[List[Dict], List[EscapeIntentAction]] = [],
                 validator: Optional[Callable] = None,
                 **kwargs):

        if isinstance(inputs[0], Dict):
            inputs = InputConfigSchema(many=True).load(inputs)

        if escape_intent_action and isinstance(escape_intent_action[0], Dict):
            escape_intent_action = EscapeIntentActionSchema(many=True).load(escape_intent_action)

        super().__init__(name, **kwargs)
        self.required_inputs = inputs
        self.entity_extractors = entity_extractors
        self.escape_intent_action = escape_intent_action
        self.validator = validator
        if not self.validator:
            self.validator = lambda v, c: None

    def inputs_mapping(self, context: ContextManager) -> Dict[Text, InputConfig]:
        mapping = {}
        for _input in self.required_inputs:
            mapping[_input.name] = _input
        return mapping

    def on_enter(self, context: ContextManager):
        node_state = {}
        node_state[STEP_COUNT] = {_input.name: 0 for _input in self.required_inputs}
        node_state[COLLECTED_INPUTS] = {}
        node_state[CURRENT_MISSING_INPUT] = ''

        params = context.get_params(self.name, {})
        node_state.update(params)

        context.set_data(self.name, node_state)

    def on_message(self, context: ContextManager) -> NodeResult:
        message_intent = context.turn_context.message.intent
        for escape_intent in self.escape_intent_action:
            if escape_intent.intent == message_intent:
                # input asking count should not increase if escape
                node_state = context.get_data(self.name)
                current_missing_input = node_state[CURRENT_MISSING_INPUT]
                node_state[STEP_COUNT][current_missing_input] -= 1

                context.turn_context.message.intent = None  # Reset intent to avoid infinite loop
                next_node = escape_intent.next_node
                if isinstance(next_node, str):
                    next_node = [next_node]
                return NodeResult(NodeStatus.ESCAPE, [self.name, *next_node])

        if self.entity_extractors:
            self.entity_extractors.process(context.turn_context.message)

        collected_inputs = self._fill_inputs(context)
        missing_input = self._get_missing_input(collected_inputs, context)
        if not missing_input:
            context.set_result(self.name, collected_inputs)
            return NodeResult(NodeStatus.DONE, self.next_node)
        else:
            self.prompt(missing_input, context)

            node_state = context.get_data(self.name)
            node_state[CURRENT_MISSING_INPUT] = missing_input.name
            node_state[STEP_COUNT][missing_input.name] += 1
            context.set_data(self.name, node_state)

            return NodeResult(NodeStatus.WAITING, self.name)

    def on_exit(self, context: ContextManager) -> None:
        node_state = context.get_data(self.name)
        node_state = {}
        context.set_data(self.name, node_state)

    def prompt(self, input_config: InputConfig, context: ContextManager) -> None:
        if not input_config.prompts:
            return
        if not input_config.reprompts:
            prompts = input_config.prompts
        else:
            node_state = context.get_data(self.name)
            if node_state[STEP_COUNT][input_config.name] > 0:
                prompts = input_config.reprompts
            else:
                prompts = input_config.prompts

        response = random.choice(prompts)
        context.add_response(Response(response))

    def _get_missing_input(self, collected_inputs: Dict[Text, Any], context: ContextManager) -> Optional[InputConfig]:
        for _input in self.required_inputs:
            if _input.name not in collected_inputs and not _input.optional:
                return _input

        # Validate all inputs
        missing_inputs = self.validator(collected_inputs, context)
        if missing_inputs:
            for iname in missing_inputs:
                collected_inputs.pop(iname)
            node_state = context.get_data(self.name)
            node_state[COLLECTED_INPUTS] = collected_inputs
            context.set_data(self.name, node_state)
            for _input in self.required_inputs:
                if _input.name not in collected_inputs and not _input.optional:
                    return _input

    def _get_intent(self, iconfig: InputMapping, message: Message) -> Optional[Text]:
        req_intents = iconfig.values
        if not req_intents:
            return message.intent

        if isinstance(req_intents, Text):
            req_intents = [req_intents]

        if message.intent in req_intents:
            return message.intent

        return None

    def _get_entities(self, iconfig: InputMapping, message: Message) -> Dict[Text, Any]:
        if not message.entities:
            return None

        req_entities = iconfig.values
        extracted_entities = {}
        single = isinstance(req_entities, Text)

        if single:
            req_entities = [req_entities]

        drop_list = []
        for i, entity in enumerate(message.entities):
            if entity.entity in req_entities:
                if (extracted_entities.get(entity.entity)):
                    if not iconfig.multiple:
                        continue
                    extracted_entities[entity.entity].append(entity.value)
                else:
                    if not iconfig.multiple:
                        extracted_entities[entity.entity] = entity.value
                    else:
                        extracted_entities[entity.entity] = [entity.value]

                if iconfig.drop:
                    drop_list.append(i)

        if iconfig.drop and drop_list:
            new_list = [entity for i, entity in enumerate(message.entities) if i not in drop_list]
            message.entities = new_list

        if single and extracted_entities:
            key = list(extracted_entities.keys())[0]
            extracted_entities = extracted_entities[key]

        return extracted_entities

    def _get_default(self, input_name: Text, imap: InputMapping, iconfig: InputConfig, context: ContextManager) -> Optional[Any]:
        if not iconfig.default:
            return None

        def _parse_default():
            default_value = iconfig.default
            if imap.itype == ITYPE.ENTITY:
                values = imap.values
                if not isinstance(values, List):
                    values = [values]
                if not set(values).isdisjoint(DUCKLING_TIME_ENTITIES) and default_value:
                    duckling = self.entity_extractors.get_extractor_by_type('DucklingExtractor')
                    if duckling:
                        datetime_entity = duckling.process(Message(default_value, timezone=context.turn_context.message.config.get('timezone')))
                        if len(datetime_entity) == 1:
                            default_value = datetime_entity[0].value
                        elif len(datetime_entity) > 1:
                            default_value = {entity.entity: entity.value for entity in datetime_entity}

            return default_value

        if iconfig.default_delay_step == 0:
            return _parse_default()

        node_state = context.get_data(self.name)
        if node_state[STEP_COUNT][input_name] >= iconfig.default_delay_step:
            return _parse_default()

        return None

    def _validate_and_assign(self,
                             input_name: Text,
                             imap: InputMapping,
                             iconfig: InputConfig,
                             value: Any,
                             validator: Callable,
                             context: ContextManager) -> Optional[Any]:
        if value:
            validated_value = validator(imap.itype, value, context)
            if validated_value:
                return validated_value
        else:
            default_value = self._get_default(input_name, imap, iconfig, context)
            if default_value:
                return default_value

    def _fill_inputs(self, context: ContextManager) -> Dict[Text, Any]:
        inputs = {}
        inputs_mapping = self.inputs_mapping(context)

        node_state = context.get_data(self.name)
        collected_inputs = node_state[COLLECTED_INPUTS]

        override_input_function = getattr(self, OVERRIDE_INPUT_FUNCTION, self._default_override_input)
        for input_name, iconfig in inputs_mapping.items():
            if node_state[STEP_COUNT][iconfig.name] == 0 and iconfig.always_ask:
                continue

            # validator take 3 arguments: itype, value, context
            validator = iconfig.validator if iconfig.validator != None else lambda t, v, c: v
            from_itype = None
            for imap in iconfig.maps:
                if node_state[STEP_COUNT][iconfig.name] == 0 and imap.always_ask:
                    continue

                if imap.itype == ITYPE.TEXT:
                    text = context.turn_context.message.text
                    # Avoid empty string for text input
                    if not text:
                        value = None
                        continue
                    value = self._validate_and_assign(input_name, imap, iconfig, text, validator, context)

                elif imap.itype == ITYPE.INTENT:
                    intent = self._get_intent(imap, context.turn_context.message)
                    value = self._validate_and_assign(input_name, imap, iconfig, intent, validator, context)

                elif imap.itype == ITYPE.ENTITY:
                    entities = self._get_entities(imap, context.turn_context.message)
                    value = self._validate_and_assign(input_name, imap, iconfig, entities, validator, context)

                if value:
                    from_itype = imap.itype
                    break

            if input_name in collected_inputs.keys() and value and from_itype in iconfig.allow_override:
                # TODO
                # Do something when previously filled input slots get override in the current message
                if collected_inputs.get(input_name) != value:
                    old_value = collected_inputs.get(input_name)
                    value = override_input_function(input_name, old_value, value, context)
                    inputs[input_name] = value

            elif input_name not in collected_inputs.keys() and value:
                inputs[input_name] = value

        if collected_inputs:
            if (inputs):
                collected_inputs.update(inputs)
                node_state[COLLECTED_INPUTS] = collected_inputs
                context.set_data(self.name, node_state)
            return collected_inputs
        else:
            if (inputs):
                node_state[COLLECTED_INPUTS] = inputs
                context.set_data(self.name, node_state)
            return inputs

    def _default_override_input(self, input_name: Text, old_value: Any, new_value: Any, context: ContextManager):
        return new_value
