from iqplace.db.fields.field import Field
from iqplace.db.fields.listfield import ListField
from iqplace.db.model import DBModel


class File(DBModel):
    collection_name = 'files'

    fileName = Field()
    user = Field()
