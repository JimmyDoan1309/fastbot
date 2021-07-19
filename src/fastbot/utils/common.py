import re
import json


def import_from_path(module_path: str):
    import importlib
    if "." in module_path:
        module_name, _, class_name = module_path.rpartition(".")
        m = importlib.import_module(module_name)
        return getattr(m, class_name)
    else:
        module = globals().get(module_path, locals().get(module_path))
        if module is not None:
            return module
        else:
            raise ImportError(f"Cannot retrieve class from path {module_path}.")


def parse_entities_from_text(text: str):
    regex = r"\[(?P<substring>[^\[\]]+)\](?P<config>\{[^\{\}]+\})"
    extra_text_len = 0
    entities = []
    for match in re.finditer(regex, text):
        group = match.groupdict()

        entity_start = match.start(1)
        entity_end = match.end(1)

        config_text = group['config']
        config = json.loads(config_text)

        substring = group['substring']
        full_text = match.group()

        text = text.replace(full_text, substring)
        entities.append({
            **config,
            'start': entity_start-extra_text_len,
            'end': entity_end-extra_text_len})
        extra_text_len += len(config_text)
    for i, e in enumerate(entities):
        e['start'] -= i*2+1
        e['end'] -= i*2+1

    return text, entities
