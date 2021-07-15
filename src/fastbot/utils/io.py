import json
from typing import Text, Dict, Any
from fastbot.schema.nlu_data import NluDataSchema
import yaml


def load_nlu_from_file(path: Text):
    with open(path, 'r') as fp:
        if path.endswith('.json'):
            data = json.load(fp)
        elif path.endswith('.yaml') or path.endswith('.yml'):
            data = yaml.load(fp, Loader=yaml.FullLoader)
        else:
            raise Exception("Flow config must be .json or .yaml file")
    return NluDataSchema().load(data)

def load_nlu_from_dict(data: Dict[Text, Any]):
    return NluDataSchema().load(data)