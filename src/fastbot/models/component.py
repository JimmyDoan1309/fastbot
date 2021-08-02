from typing import Text, Dict, Any


class ComponentConfig:
    def __init__(self, name: Text, type: Text, arguments: Dict[Text, Any] = {}):
        self.name = name
        self.type = type
        self.arguments = arguments
