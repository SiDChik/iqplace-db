from db.field import Field
from db.model import DBModel


class User(DBModel):
    phone_number = Field()