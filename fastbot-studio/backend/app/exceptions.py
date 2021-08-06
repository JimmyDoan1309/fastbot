from fastapi import HTTPException


class BotNotFoundException(HTTPException):
    def __init__(self, bot_id: str):
        super().__init__(404, f'botId `{bot_id}` does not exist.')
