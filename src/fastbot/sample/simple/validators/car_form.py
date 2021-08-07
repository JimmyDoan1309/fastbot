from fastbot.dialog.context import ContextManager
from fastbot.models import Response


def car_year_validate(itype: str, value: any, context: ContextManager):
    year = int(value)
    if year < 1980 or year > 2022:
        context.add_response(Response('We only able to search for car year model between 1980 and 2022'))
        return None
    return value
