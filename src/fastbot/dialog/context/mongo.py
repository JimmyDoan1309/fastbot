from . import TurnContext
from .memory import MemoryContextManager
from fastbot.models import Message
from fastbot.schema.policy_data import StepSchema
from typing import Text, Dict, Any, Union, List
from pymongo.collection import Collection
from time import time
import json
import pymongo


DB_NAME = 'fastbot'
CONTEXT_COLLECTION_NAME = 'contexts'
USERDATA_COLLECTION_NAME = 'users'


class MongoContextMananger(MemoryContextManager):
    def __init__(self, uri: Text = None, **kwargs):
        super().__init__()
        if uri:
            self.client = pymongo.MongoClient(uri)
            self.db = self.client.get_database(DB_NAME)
            self.contexts_col = self.db.get_collection(CONTEXT_COLLECTION_NAME)
            self.users_col = self.db.get_collection(USERDATA_COLLECTION_NAME)
        else:
            self.contexts_col = kwargs.get('contexts_col')
            self.users_col = kwargs.get('users_col')
        assert self.contexts_col, "No Mongo collection reference!"

    def init(self, _id: Text):
        ctx = self.__class__(contexts_col=self.contexts_col, users_col=self.users_col)
        ctx._id = _id
        exist = ctx.contexts_col.find_one({'_id': _id})
        if not exist:
            ctx.contexts_col.insert_one({'_id': _id, 'data': ctx.json()})

        exist = ctx.users_col.find_one({'_id': _id})
        if not exist:
            ctx.users_col.insert_one({'_id': _id, 'data': ctx.user_data})

        return ctx

    def load(self):
        context_data = self.contexts_col.find_one({'_id': self._id}).get('data', {})
        self.callstack = context_data.get('callstack', [])
        self.node_params = context_data.get('node_params', {})
        self.node_results = context_data.get('node_results', {})
        self.node_data = context_data.get('node_data', {})
        self.node_status = context_data.get('node_status', {})
        self.timestamp = context_data.get('time_stamp', time())
        user_data = self.users_col.find_one({'_id': self._id}).get('data', {})
        self.user_data = user_data.get('user_data', {})

        history = context_data.get('history', [])
        self.history = StepSchema(many=True).load(history)

    def save(self):
        dump = self.json()
        self.contexts_col.update_one({'_id': self._id}, {'$set': {'data': dump}})
        self.users_col.update_one({'_id': self._id}, {'$set': {'data': self.user_data}})
