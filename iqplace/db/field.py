class Field:
    required = False

    value = None

    def __init__(self, required=False):
        self.required = required
        pass

    def validate(self):
        return True
