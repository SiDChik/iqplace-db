from iqplace.db import Field
from iqplace.db import DBModel


class User(DBModel):
    phone_number = Field()