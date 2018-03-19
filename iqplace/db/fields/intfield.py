from iqplace.db.exceptions import ValidationError
from iqplace.db.fields.field import Field


class INTField(Field):
    def validate_value(self, value):
        if isinstance(value, int):
            return True
        raise ValidationError('%s is not integer' % self.attr_name)
