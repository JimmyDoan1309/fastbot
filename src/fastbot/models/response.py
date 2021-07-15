from typing import Text, Any


class Response:
    def __init__(self, type: Text, content: Any):
        self.type = type
        self.content = content
        self.watermark = None
