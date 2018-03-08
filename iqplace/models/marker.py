from iqplace.db.field import Field
from iqplace.db.model import DBModel


class Marker(DBModel):
    latitude = Field()
    longitude = Field()

