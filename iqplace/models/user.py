from iqplace.db.fields.field import Field
from iqplace.db.fields.listfield import ListField
from iqplace.db.model import DBModel


class User(DBModel):
    collection_name = 'users'

    phone = Field()
    email = Field()
    login = Field()

    groups = ListField()

    firstName = Field()
    lastName = Field()

    avatar = Field()

    password = Field()
    salt = Field()
    tokens = Field()

    vk = Field()
    fb = Field()

    def __init__(self, *args, **kwargs):
        kwargs['groups'] = kwargs.get('groups', None) or ['user']
        
        super(User, self).__init__(*args, **kwargs)