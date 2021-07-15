from fastbot.models import Message


class Extractor:
    name = 'Extractor'

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', self.name)
        self.type = self.__class__.__name__

    def process(self, message: Message):
        raise NotImplementedError()
