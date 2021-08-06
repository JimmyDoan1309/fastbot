import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://admin:admin@localhost:27017')

_mongo_client = AsyncIOMotorClient(MONGO_URI)
mongodb = _mongo_client['fastbot-studio']
