import json
from typing import Text, Dict, Any, Union
from fastbot.schema.nlu_data import NluDataSchema
import yaml


def load_nlu_data(data: Union[Text, Dict[Text, Any]]):
    if isinstance(data, str):
        path = data
        with open(path, 'r') as fp:
            if path.endswith('.json'):
                data = json.load(fp)
            elif path.endswith('.yaml') or path.endswith('.yml'):
                data = yaml.load(fp, Loader=yaml.FullLoader)
            else:
                raise Exception("Flow config must be .json or .yaml file")
    return NluDataSchema().load(data)
