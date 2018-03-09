import rapidjson

from iqplace.db.exceptions import FieldDoesntExist, ValidationError
from iqplace.db.fields.field import Field
from iqplace.db.fields.idfield import IDField
from iqplace.db.manager import DBManager
from iqplace.helpers import json_default


class ModelMeta(type):
    def __new__(cls, name, bases, dickt):
        cc = super(ModelMeta, cls).__new__(cls, name, bases, dickt)
        if 'Meta' not in dickt or not dickt['Meta']().abstract:
            cc.manager = DBManager(model=cc)
        return cc


class DBModel(metaclass=ModelMeta):
    id = None
    collection_name = None
    manager = None
    fields = None
    collection = None
    __diff_keys = None

    def __init__(self, **initial_data):
        self.__diff_keys = set()
        self.fields = {}

        # add _id Field
        setattr(self, 'id', IDField(db_field='_id'))

        # init fields
        for attr_name in dir(self):
            if attr_name.startswith('_'):
                continue
            attr = getattr(self, attr_name, None)
            if isinstance(attr, Field):
                attr.attr_name = attr_name

                if not attr.db_field:
                    attr.db_field = attr_name

                self.fields[attr_name] = attr
                initial_value = initial_data.pop(attr_name)
                attr.set_value(initial_value)
            else:
                raise FieldDoesntExist

        if initial_data:
            raise ValidationError('%s unknown fields' % (', '.join(list(initial_data.keys()))))

    def __getattribute__(self, item):
        if hasattr(self, item):
            attr = super(DBModel, self).__getattribute__(item)
            if isinstance(attr, Field):
                return attr.value
            return attr
        raise AttributeError

    def __setattr__(self, key, value):
        is_field = False
        if hasattr(self, key):
            attr = super(DBModel, self).__getattribute__(key)
            if isinstance(attr, Field):
                is_field = True
                if value != attr.value:
                    self.__diff_keys.add(key)
                    attr.set_value(value)
        if not is_field:
            super(DBModel, self).__setattr__(key, value)

    def to_db(self, fields=None):
        out = {}
        for field in self.fields.values():
            if fields and field not in fields:
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

    async def save(self):
        if not self.id:
            inserted = await self.manager.create()
            self.id = inserted.id
        elif self.__diff_keys:
            await self.manager.update_by_id(self.id, self, self.to_db(self.__diff_keys))
            self.__diff_keys = set()
