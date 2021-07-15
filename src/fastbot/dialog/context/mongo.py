from . import TurnContext
from .memory import MemoryContextManager
from fastbot.models import Message
from typing import Text, Dict, Any, Union, List
from pymongo.collection import Collection
import pymongo


DB_NAME = 'fastbot'
COLLECTION_NAME = 'context'


class MongoContextMananger(MemoryContextManager):
    def __init__(self, uri: Text = None, **kwargs):
        super().__init__()
        if uri:
            self.client = pymongo.MongoClient(uri)
            self.db = self.client.get_database(DB_NAME)
            self.col = self.db.get_collection(COLLECTION_NAME)
        else:
            self.col = kwargs.get('collection_ref')

        assert self.col, "No Mongo collection reference!"

    def init(self, _id: Text):
        ctx = self.__class__(collection_ref=self.col)
        ctx._id = _id
        exist = ctx.col.find_one({'_id': _id})
        if not exist:
            ctx.col.insert_one({'_id': _id, 'data': ctx.json()})
        return ctx

    def load(self):
        data = self.col.find_one({'_id': self._id}).get('data', {})
        self.callstack = data.get('callstack', [])
        self.history = data.get('history', [])
        self.node_params = data.get('node_params', {})
        self.node_results = data.get('node_results', {})
        self.node_data = data.get('node_data', {})
        self.node_status = data.get('node_status', {})

    def save(self):
        dump = self.json()
        self.col.update_one({'_id': self._id}, {'$set': {'data': dump}})
