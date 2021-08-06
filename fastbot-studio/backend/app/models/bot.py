from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.utils.common import to_camel, generate_uuid


class BotCreateConfig(BaseModel):
    timezone: Optional[str] = 'UTC'
    name: str = 'Alexa'
    language: str = 'en'
    avatar_url: Optional[str] = 'https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png'

    class Config:
        alias_generator = to_camel


class BotUpdateConfig(BaseModel):
    timezone: Optional[str]
    name: Optional[str]
    language: Optional[str]
    avatar_url: Optional[str]

    class Config:
        alias_generator = to_camel


class BotGetConfig(BotCreateConfig):
    bot_id: str = Field(default_factory=generate_uuid)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        alias_generator = to_camel


class BotFullConfig(BotGetConfig):
    data: Optional[dict] = {}
