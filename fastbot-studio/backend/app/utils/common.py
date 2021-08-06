from uuid import uuid4


def to_camel(string: str) -> str:
    words = string.split('_')
    if len(words) == 1:
        return words[0]
    else:
        return words[0]+''.join(w.capitalize() for w in words[1:])


def generate_uuid() -> str:
    return str(uuid4())
