import rapidjson

from pip.utils import cached_property

from iqplace.db.exceptions import FieldDoesntExist, ValidationError
from iqplace.db.fields.field import Field
from iqplace.db.fields.idfield import IDField
from iqplace.db.manager import DBManager
from iqplace.helpers import json_default, deepcopy


class ModelMeta(type):
    def __new__(cls, name, bases, dickt):
        cc = super(ModelMeta, cls).__new__(cls, name, bases, dickt)
        if 'Meta' not in dickt or not dickt['Meta']().abstract:
            cc.manager = DBManager(model=cc)
        return cc


class DBModel(metaclass=ModelMeta):
    id = IDField(db_field='_id')
    collection_name = None
    manager = None  # type: DBManager
    fields = None
    __diff_keys = None

    def __init__(self, from_db=False, **initial_data):
        self.__diff_keys = set()
        self.fields = {}

        cls = self.__class__
        # init fields
        for attr_name in dir(cls):
            if attr_name.startswith('_'):
                continue
            attr = getattr(cls, attr_name, None)
            if isinstance(attr, Field):
                attr = attr.__class__(*attr._args, **attr._kwargs)
                attr.attr_name = attr_name

                if not attr.db_field:
                    attr.db_field = attr_name

                self.fields[attr_name] = attr

                if from_db:
                    initial_value = initial_data.pop(attr.db_field, None)
                else:
                    initial_value = initial_data.pop(attr_name, None)

                attr.set_value(initial_value)
            elif attr_name in initial_data:
                raise FieldDoesntExist

        if initial_data:
            raise ValidationError('%s unknown fields' % (', '.join(list(initial_data.keys()))))

    def __getattribute__(self, item):
        attr = super(DBModel, self).__getattribute__(item)
        if isinstance(attr, Field) and item in self.fields:
            return self.fields[item].value
        return attr

    def __setattr__(self, key, value):
        is_field = False
        attr = super(DBModel, self).__getattribute__(key)
        if isinstance(attr, Field):
            attr = self.fields[key]
            is_field = True
            if value != attr.value:
                self.__diff_keys.add(key)
                attr.set_value(value)

        if not is_field:
            super(DBModel, self).__setattr__(key, value)

    @cached_property
    def collection(self):
        return self.manager.collection

    def from_db(self, **data):
        out = {}
        for field in self.fields.values():
            value = data.get(field.attr_name, None)
            out[field.attr_name] = value
        return out

    def to_db(self, fields=None):
        out = {}
        for field in self.fields.values():
            if fields and field.attr_name not in fields:
                continue
            out[field.db_field] = field.db_value

        return out

    def validate(self):
        for field in self.fields.values():
            field.validate()
        return True

    def to_dict(self):
        out = {}
        for field in self.fields.values():
            out[field.db_field] = field.value

        return out

    def serialize(self):
        out = {}
        for field in self.fields.values():
            out[field.db_field] = field.serialize_value

        return out

    def to_json(self):
        return rapidjson.dumps(self.serialize(), default=json_default)

    async def delete(self):
        await self.manager.delete(self.id)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def update_db(self, **kwargs):
        self.update(**kwargs)
        await self.save()

    async def save(self):
        if not self.id:
            data = self.to_db()
            del data['_id']
            inserted = await self.manager.create(**data)
            self.id = inserted.id
        elif self.__diff_keys:
            await self.manager.update_by_id(self.id, self.to_db(self.__diff_keys))
        self.__diff_keys = set()
