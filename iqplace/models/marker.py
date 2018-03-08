from db.field import Field
from db.model import DBModel


class Marker(DBModel):
    latitude = Field()
    longitude = Field()

