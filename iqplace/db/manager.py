from bson import ObjectId
from pip.utils import cached_property
from pymongo import ASCENDING

from iqplace.app import IQPlaceApp
from iqplace.db.exceptions import ObjectDoesntExist


class DBManager():
    model = None

    def __init__(self, model):
        self.model = model

    @cached_property
    def collection(self):
        return IQPlaceApp().db[self.model.collection_name]

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

    async def delete(self, pk):
        return await self.collection.remove({'_id': ObjectId(pk)})

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
            return self.model(res)

    async def find(self, params=None, sort_params=None, limit=None, skip=None):
        params = params or {}

        res = self.collection.find(params)
        if sort_params:
            res = res.sort(sort_params)

        if skip:
            res = res.skip(skip)

        if limit:
            res = res.limit(limit)

        res = [self.model(from_db=True, **obj) for obj in await res.to_list(None)]
        return res

    async def create(self, **data):
        insert_result = await self.collection.insert_one(data)
        obj = await self.collection.find_one({'_id': insert_result.inserted_id})
        return self.model(from_db=True, **obj)
