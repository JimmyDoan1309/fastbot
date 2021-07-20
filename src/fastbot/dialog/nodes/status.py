from typing import Text, List, Union
from enum import Enum


class NodeStatus(str, Enum):
    READY = 'ready'
    BEGIN = 'begin'
    WAITING = 'waiting'
    DONE = 'done'
    ERROR = 'error'
    RESTART = 'restart'


class NodeResult:
    def __init__(self, status: NodeStatus, next_node: Union[Text, List[Text]] = None):
        if not isinstance(status, NodeStatus):
            raise Exception('status must of type NodeStatus')
        self.status = status
        self.next = next_node
