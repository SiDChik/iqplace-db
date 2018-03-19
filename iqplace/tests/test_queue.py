import asyncio

from iqplace.db.fields.field import Field
from iqplace.db.model import DBModel
from iqplace.tests.base import TestCase


class SimpleTestModel(DBModel):
    collection_name = 'test_model'

    field1 = Field()


class TestCase(TestCase):
    async def test_queue(self):
        await SimpleTestModel.manager.to_queue('test')
        print('done')
