from pymongo import ASCENDING, DESCENDING

from iqplace.db.fields.field import Field
from iqplace.db.fields.intfield import INTField
from iqplace.db.model import DBModel
from iqplace.tests.base import TestCase


class SimpleTestModel(DBModel):
    collection_name = 'test_model'

    field1 = Field()


class SimpleTestSortModel(DBModel):
    collection_name = 'test_model_sort'

    int = INTField()


class ModelTest(TestCase):
    async def test_create_model(self):
        test = SimpleTestModel(field1='test_value')

        self.assertIsInstance(test, SimpleTestModel)
        self.assertEqual(test.field1, 'test_value')

    async def test_update_model(self):
        test = await SimpleTestModel.manager.create(field1='vasya')
        test.field1 = 'ivan'
        await test.save()

        check = await SimpleTestModel.manager.get_by_id(test.id)
        self.assertEqual(check.field1, 'ivan')

        test.update(field1='trololo')
        await test.save()
        check = await SimpleTestModel.manager.get_by_id(test.id)
        self.assertEqual(check.field1, 'trololo')

        await test.update_db(field1='123')
        check = await SimpleTestModel.manager.get_by_id(test.id)
        self.assertEqual(check.field1, '123')

    async def test_save_model(self):
        test = SimpleTestModel(field1='test_value')

        await test.save()

        self.assertIsNotNone(test.id)

    async def test_get_model(self):
        test = SimpleTestModel(field1='test_value')

        await test.save()

        self.assertIsNotNone(test.id)

        find_by_id = await SimpleTestModel.manager.get_by_id(test.id)

        self.assertEqual(find_by_id.id, test.id)
        self.assertEqual(find_by_id.field1, test.field1)

    async def test_find(self):
        test1 = await SimpleTestModel.manager.create(field1='hello')
        test2 = await SimpleTestModel.manager.create(field1='world')

        self.assertIsNotNone(test1.id)
        self.assertIsNotNone(test2.id)

        hellos = await SimpleTestModel.manager.find({
            'field1': 'hello'
        })
        worlds = await SimpleTestModel.manager.find({
            'field1': 'world'
        })

        self.assertEqual(len(hellos), 1)
        self.assertEqual(hellos[0].id, test1.id)
        self.assertEqual(len(worlds), 1)
        self.assertEqual(worlds[0].id, test2.id)

    async def test_pagination_sort(self):
        for index in range(100):
            await SimpleTestSortModel.manager.create(int=index)

        # Ascending
        sort_ascend = await SimpleTestSortModel.manager.find(sort_params=('int', ASCENDING))
        self.assertEqual(len(sort_ascend), 100)
        for i in range(100):
            self.assertEqual(sort_ascend[i].int, i)

        # Descending
        sort_descend = await SimpleTestSortModel.manager.find(sort_params=('int', DESCENDING))
        self.assertEqual(len(sort_descend), 100)
        for i in range(100):
            self.assertEqual(sort_descend[i].int, 99 - i)

        # pagination
        sort_ascend = await SimpleTestSortModel.manager.find(sort_params=('int', ASCENDING), per_page=10, page=0)
        self.assertEqual(sort_ascend[0].int, 0)
        self.assertEqual(sort_ascend[-1].int, 9)
        sort_ascend = await SimpleTestSortModel.manager.find(sort_params=('int', ASCENDING), per_page=10, page=5)
        self.assertEqual(sort_ascend[0].int, 50)
        self.assertEqual(sort_ascend[-1].int, 59)
