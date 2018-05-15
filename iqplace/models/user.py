import rapidjson

from iqplace.db.fields.field import Field
from iqplace.db.fields.listfield import ListField
from iqplace.db.model import DBModel
from iqplace.helpers import json_default


class User(DBModel):
    collection_name = 'users'

    phone = Field()
    email = Field()
    login = Field()

    groups = ListField()

    fio = Field()

    firstName = Field()
    lastName = Field()

    sex = Field()

    avatar = Field()

    password = Field()
    salt = Field()
    tokens = Field()

    vk = Field()
    fb = Field()

    def public_json(self):
        serialize = self.serialize()

        serialize.pop('password', None)
        serialize.pop('salt', None)

        return rapidjson.dumps(self.serialize(), default=json_default)

    def __init__(self, *args, **kwargs):
        kwargs['groups'] = kwargs.get('groups', None) or ['user']
        
        super(User, self).__init__(*args, **kwargs)