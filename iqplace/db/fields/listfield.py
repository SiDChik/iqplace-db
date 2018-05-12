from iqplace.db.exceptions import ValidationError
from iqplace.db.fields.field import Field


class ListField(Field):
    def validate_value(self, value):
        if isinstance(value, list):
            return True
        raise ValidationError('%s is not list' % self.attr_name)
