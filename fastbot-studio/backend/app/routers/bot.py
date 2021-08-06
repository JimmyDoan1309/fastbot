from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from app.dependencies import get_bot_collection, pagination
from app.models.bot import BotGetConfig, BotCreateConfig, BotUpdateConfig, BotFullConfig
from app.exceptions import BotNotFoundException
from datetime import datetime
import uuid


router = APIRouter(
    prefix='/bot',
    tags=['bot'],
)


@router.post('/create', response_model=BotGetConfig)
async def create_bot(bot: BotCreateConfig, bot_collection=Depends(get_bot_collection)):
    new_bot = BotGetConfig(**bot.dict(by_alias=True))
    await bot_collection.insert_one(new_bot.dict(by_alias=True))
    return new_bot


@router.get('/', response_model=List[BotGetConfig])
async def get_all_bots(query=Depends(pagination), bot_collection=Depends(get_bot_collection)):
    bots = await bot_collection.find().skip(query.skip).to_list(query.limit)
    return bots


@router.get('/{botId}', response_model=BotFullConfig)
async def get_bot_by_id(botId: str, bot_collection=Depends(get_bot_collection)):
    exist = await bot_collection.find_one({'botId': botId})
    if not exist:
        raise BotNotFoundException(botId)
    return exist


@router.put('/{botId}', response_model=BotGetConfig)
async def update_bot_config(botId: str, bot: BotUpdateConfig, bot_collection=Depends(get_bot_collection)):
    exist = await bot_collection.find_one({'botId': botId})
    if not exist:
        raise BotNotFoundException(botId)

    updated_fields = bot.dict(by_alias=True)
    none = []
    for k in list(updated_fields.keys()):
        if updated_fields[k] is None:
            none.append(k)
    for k in none:
        updated_fields.pop(k)
    updated_fields['updatedAt'] = datetime.now()

    await bot_collection.update_one(
        {'botId': botId},
        {'$set': updated_fields}
    )
    result = await bot_collection.find_one({'botId': botId})
    return result


@router.post('/{botId}/data')
async def save_bot_data(botId: str, data: dict, bot_collection=Depends(get_bot_collection)):
    exist = await bot_collection.find_one({'botId': botId})
    if not exist:
        raise BotNotFoundException(botId)
    await bot_collection.update_one(
        {'botId': botId},
        {'$set': {'data': data, 'updatedAt': datetime.now()}}
    )
    return {'success': True}


@router.delete('/{botId}')
async def delete_bot_by_id(botId: str, bot_collection=Depends(get_bot_collection)):
    result = await bot_collection.delete_one({'botId': botId})
    if result.deleted_count < 1:
        raise BotNotFoundException(botId)
    return {'success': True}
