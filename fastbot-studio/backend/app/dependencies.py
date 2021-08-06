from .db import mongodb, AsyncIOMotorCollection
from .models.query import Pagination
from typing import Optional
from fastapi import HTTPException


async def get_bot_collection() -> AsyncIOMotorCollection:
    return mongodb['bot']


async def pagination(skip: int = 0, limit: int = 10) -> Pagination:
    if skip < 0 or limit < 1:
        raise HTTPException(status_code=400, detail='`skip` must greater than 0 and `limit` must greater than 1.')
    return Pagination(skip=skip, limit=limit)
