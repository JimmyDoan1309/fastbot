from typing import Text, List, Union


class NodeStatus:
    READY = 0
    BEGIN = 1
    WAITING = 2
    DONE = 3
    ERROR = 4
    RESTART = 5


class NodeResult:
    def __init__(self, status: int, next_node: Union[Text, List[Text]] = None):
        self.status = status
        self.next = next_node
