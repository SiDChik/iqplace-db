from iqplace.db import Field
from iqplace.db import DBModel


class Marker(DBModel):
    latitude = Field()
    longitude = Field()

