from iqplace.db.fields.field import Field
from iqplace.db.model import DBModel
from iqplace.tests.base import TestCase


class SimpleTestModel(DBModel):
    collection_name = 'test_model'

    field1 = Field()

class ModelTest(TestCase):
    async def test_create_model(self):
        test = SimpleTestModel(field1='test_value')

        self.assertIsInstance(test, SimpleTestModel)
        self.assertEqual(test.field1, 'test_value')

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
