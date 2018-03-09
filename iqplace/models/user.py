from iqplace.db.fields.field import Field
from iqplace.db.model import DBModel


class User(DBModel):
    phone_number = Field()
