from iqplace.db.manager import DBManager


class ModelMeta(type):
    def __new__(cls, name, bases, dickt):
        cc = super(ModelMeta, cls).__new__(cls, name, bases, dickt)
        if 'Meta' not in dickt or not dickt['Meta']().abstract:
            cc.manager = DBManager(model=cc)
        return cc


class DBModel(metaclass=ModelMeta):
    collection_name = None
    manager = None
    fields = None
    collection = None

    def __init__(self, **initial_data):
        for key, value in initial_data.items():
            setattr(self, key, value)
        self.fields = {}
