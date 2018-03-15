from bson import ObjectId

from iqplace.db.exceptions import ValidationError
from iqplace.db.fields.field import Field


class IDField(Field):
    def validate_value(self, value):
        if not isinstance(value, ObjectId):
            raise ValidationError('%s is not ObjectId' % self.attr_name)
        return super(IDField, self).validate_value(value)

    def set_value(self, value, silent=False):
        if value:
            self.validate_value(value)
        self.value = value
