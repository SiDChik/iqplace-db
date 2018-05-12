from iqplace.db.fields.field import Field
from iqplace.db.fields.listfield import ListField
from iqplace.db.model import DBModel


class Marker(DBModel):
    collection_name = 'markers'
    name = Field()
    group = Field()
    address = Field()
    description = Field()

    price = Field()

    author = Field()

    latitude = Field()
    longitude = Field()

    images = ListField()

    fromDate = Field()
    toDate = Field()