from typing import Text, Any


class Response:
    def __init__(self, content: Any, type: Text = 'text'):
        self.type = type
        self.content = content
        self.watermark = None
