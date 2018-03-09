from iqplace.db.exceptions import ValidationError


class Field:
    required = False

    value = None
    db_field = None
    attr_name = None

    def __init__(self, required=False, db_field=None):
        self.required = required
        self.db_field = None
        pass

    def get_serialize_value(self):
        return self.value

    def set_value(self, value, silent=False):
        self.validate_value(value)
        self.value = value

    def validate_value(self, value):
        if value is None and self.required:
            raise ValidationError('%s is required' % self.attr_name)
        return True

    def validate(self):
        return self.validate_value(self.value)

    @property
    def db_value(self):
        return self.value

    @property
    def serialize_value(self):
        return self.get_serialize_value()
