import asyncio
from functools import partial

from bson import ObjectId
from pymongo import ASCENDING

from iqplace.db.exceptions import ObjectDoesntExist
from cached_property import cached_property

class DBManager():
    model = None

    def __init__(self, model):
        self.model = model

    @cached_property
    def collection(self):
        from iqplace.app import IQPlaceApp
        return IQPlaceApp().get_collection(self.model.collection_name)

    async def list(self, query=None, page=None, per_page=None, sort_key=None):
        if query is None:
            query = {}

        cursor = await self.collection.find(query)
        dicts = self.paginate(cursor, page, per_page, sort_key).to_list(None)
        out = []
        for data in dicts:
            out.append(self.model(**data))
        return out

    def paginate(self, cursor, page=None, per_page=None, sort_key=None):
        if sort_key:
            cursor = cursor.sort(sort_key, direction=ASCENDING)
        if page is not None and per_page:  # pages are zero-indexed
            cursor = cursor.skip(page * per_page).limit(per_page)
        return cursor

    async def delete_by_id(self, pk):
        return await self.delete({'_id': ObjectId(pk)})

    async def delete(self, criteria):
        return await self.collection.remove(criteria)

    async def get_by_id(self, pk, ):
        query = {'_id': ObjectId(pk)}

        data = await self.collection.find_one(query)
        if data:
            return self.model(from_db=True, **data)
        else:
            raise ObjectDoesntExist

    async def update_by_id(self, pk, data):
        query = {'_id': ObjectId(pk)}

        res = await self.collection.update_one(query, {'$set': data})
        if res.matched_count != 1 or res.modified_count != 1:
            raise AssertionError('cant update')

        return await self.get_by_id(pk)

    async def find_one(self, params):
        res = await self.collection.find_one(params)
        if res:
            return self.model(from_db=True, **res)

    async def find(self, query=None, sort_params=None, per_page=None, page=None):
        query = query or {}

        res = self.collection.find(query)
        if sort_params:
            res = res.sort(*sort_params)

        if per_page:
            per_page = max(1, per_page)
            page = page or 0
            res = res.skip(per_page * page)
            res = res.limit(per_page)

        res = await res.to_list(None)
        res = [self.model(from_db=True, **obj) for obj in res]
        return res

    async def create(self, **data):
        insert_result = await self.collection.insert_one(data)
        obj = await self.collection.find_one({'_id': insert_result.inserted_id})
        return self.model(from_db=True, **obj)

    @property
    def queue(self):
        from iqplace.app import IQPlaceApp
        return IQPlaceApp().queue

    async def to_queue(self, message):
        await asyncio.sleep(1)
        reader, writer = await asyncio.open_unix_connection(path='/tmp/queue.sock')

        writer.write(message.encode())

        raw_resp = await reader.readline()
        print(raw_resp)
