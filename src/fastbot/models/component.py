from typing import Text, Dict, Any


class ComponentConfig:
    def __init__(self, name: Text, type: Text, arguements: Dict[Text, Any] = {}):
        self.name = name
        self.type = type
        self.arguements = arguements
