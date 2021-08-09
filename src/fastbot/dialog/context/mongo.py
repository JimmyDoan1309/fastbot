from . import TurnContext
from .memory import MemoryContextManager
from fastbot.models import Message
from fastbot.schema.policy_data import StepSchema
from typing import Text, Dict, Any, Union, List
from time import time, sleep
from uuid import uuid4
from pymongo import ReturnDocument
from random import random
import json
import pymongo
import os


DB_NAME = 'fastbot'
CONTEXT_COLLECTION_NAME = 'contexts'
USERDATA_COLLECTION_NAME = 'users'
MONGO_CONTEXT_LOCK_TIMEOUT = os.getenv('MONGO_CONTEXT_LOCK_TIMEOUT', 10)


class MongoContextMananger(MemoryContextManager):
    def __init__(self, uri: Text = None, **kwargs):
        super().__init__(**kwargs)
        if uri:
            self.client = pymongo.MongoClient(uri)
            self.db = self.client.get_database(DB_NAME)
            self.contexts_col = self.db.get_collection(CONTEXT_COLLECTION_NAME)
            self.users_col = self.db.get_collection(USERDATA_COLLECTION_NAME)
        else:
            self.contexts_col = kwargs.get('contexts_col')
            self.users_col = kwargs.get('users_col')
        assert self.contexts_col, "No Mongo contexts collection reference!"
        assert self.users_col, "No Mongo users collection reference"
        self.timeout_after = kwargs.get('timeout_after', MONGO_CONTEXT_LOCK_TIMEOUT)

    def init(self, user_id: Text = None, conversation_id: Text = None, user_data: Dict[Text, Any] = {}):
        ctx = self.__class__(
            contexts_col=self.contexts_col,
            users_col=self.users_col,
            user_id=user_id,
            conversation_id=conversation_id,
            user_data=user_data,
            response_function=self.response_function,
            timeout_after=self.timeout_after,
        )
        exist = ctx.contexts_col.find_one({'_id': ctx._id})
        if not exist:
            ctx.contexts_col.insert_one({
                '_id': ctx._id,
                'data': ctx.to_dict(),
                'lockQueue': [],
                'lockTimeout': 0,
                'lockOwner': None,
            })

        exist = ctx.users_col.find_one({'_id': user_id})
        if not exist:
            ctx.users_col.insert_one({'_id': user_id, 'data': ctx.user_data})

        return ctx

    def update_user_data(self, user_id: Text, data: Dict[Text, Any] = {}):
        assert isinstance(data, dict), 'user_data must be a json-serializable python dictionary'

        exist = self.users_col.find_one({'_id': user_id})
        if not exist:
            self.users_col.insert_one({'_id': user_id, 'data': data})
        else:
            user_data = self.users_col.find_one({'_id': self.user_id}).get('data', {})
            user_data.update(data)
            self.users_col.update_one({'_id': user_id}, {'$set': {'data': user_data}})

    def get_context_and_lock(self, message_id: str):
        # Try to acquire the lock
        context_data = self.contexts_col.find_one_and_update(
            {'_id': self._id, '$or': [
                {'$or': [
                    {'$and': [
                        {'lockQueue.0': message_id},
                        {'lockOwner': None}]},
                    {'$and': [
                        {'lockQueue': {'$size': 0}},
                        {'lockOwner': None}]}]},
                {'lockTimeout': {'$lt': time()}}]},
            {'$set': {'lockTimeout': time()+self.timeout_after, 'lockOwner': message_id}, '$pull': {'lockQueue': message_id}},
            return_document=ReturnDocument.AFTER)

        # Add instanceId to queue for lock fairness
        if context_data is None:
            self.contexts_col.find_one_and_update({'_id': self._id}, {'$push': {'lockQueue': message_id}})

        # Retry acquire the lock after a random amount of time to avoid split brain
        # where two instance try to acquire the lock at the sametime therefor both fail
        while context_data is None:
            wait = 0.05+random()/4  # wait between 50ms ~ 300ms before try again
            sleep(wait)
            context_data = self.contexts_col.find_one_and_update(
                {'_id': self._id, '$or': [
                    {'$or': [
                        {'$and': [
                            {'lockQueue.0': message_id},
                            {'lockOwner': None}]},
                        {'$and': [
                            {'lockQueue': {'$size': 0}},
                            {'lockOwner': None}]}]},
                    {'lockTimeout': {'$lt': time()}}]},
                {'$set': {'lockTimeout': time()+self.timeout_after, 'lockOwner': message_id}, '$pull': {'lockQueue': message_id}},
                return_document=ReturnDocument.AFTER)

        return context_data.get('data', {})

    def load(self, message_id: Text):
        context_data = self.get_context_and_lock(message_id)
        self.callstack = context_data.get('callstack', [])
        self.node_params = context_data.get('node_params', {})
        self.node_results = context_data.get('node_results', {})
        self.node_data = context_data.get('node_data', {})
        self.node_status = context_data.get('node_status', {})
        self.timestamp = context_data.get('time_stamp', time())

        user_data = self.users_col.find_one({'_id': self.user_id}).get('data', {})
        self.user_data = user_data

        history = context_data.get('history', [])
        self.history = StepSchema(many=True).load(history)

    def save(self, message_id: Text):
        dump = self.to_dict()
        self.contexts_col.update_one(
            {'_id': self._id, 'lockOwner': message_id},
            {'$set': {
                'data': dump,
                'lockTimeout': time()+self.timeout_after,
                'lockOwner': None,
            }}
        )
        self.users_col.update_one({'_id': self.user_id}, {'$set': {'data': self.user_data}})
