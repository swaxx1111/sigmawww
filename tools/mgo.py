#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/31 4:39 PM
# @Author  : wangdongming
# @Site    : 
# @File    : mgo.py
# @Software: Hifive
import os
import pymongo
from bson import ObjectId


class MongoClient(object):

    def __init__(self, **db_settings):
        host = db_settings.get('host') or os.getenv('MgoHost')
        port = db_settings.get('port') or os.getenv('MgoPort') or 27017
        username = db_settings.get('username') or os.getenv('MgoUser')
        pwd = db_settings.get('password') or os.getenv('MgoPass')
        timeout = db_settings.get('timeout') or 3

        database = db_settings.get('database') or os.getenv('MgoDB') or 'draw-ai'
        collection = db_settings.get('collection') or os.getenv('MgoCollect') or 'tasks'
        if not host:
            raise EnvironmentError('cannot found mongo host')
        if username and pwd:
            self.client = pymongo.MongoClient(
                host=host,
                port=int(port),
                connect=False,  # False 在第一次操作的时候实时连接
                serverSelectionTimeoutMS=timeout*1000,
                connectTimeoutMS=5000,
                socketTimeoutMS=timeout*1000,
                appname='ai-draw-prof'
            )
            self.db = self.client[database]
            self.db.authenticate(username, pwd)
        else:
            self.client = pymongo.MongoClient(host, port)
            self.db = self.client[database]
        self.collect = self.db[collection]

    def _get_query(self, data):
        query = {}
        if '_id' in data:
            query['_id'] = ObjectId(data['_id'])
            del data['_id']
        else:
            query = data
        return query

    def update(self, query, data, upsert=True, multi=True):
        # query = self._get_query(data)
        if multi:
            res = self.collect.update_many(query, data, upsert)
        else:
            res = self.collect.update_one(query, data, upsert)
        return res

    def insert(self, data):
        query = self._get_query(data)
        exist = self.collect.find_one(query)
        if not exist:
            self.collect.insert(data)

    def get_all(self):
        return self.collect.find()

    def remove(self, data):
        if isinstance(data, dict):
            query = self._get_query(data)
            self.collect.remove(data)

    def get_count(self, query):
        return self.collect.find(query).count()

    def close(self):
        self.client.close()
