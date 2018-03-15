import os

from motor.motor_asyncio import AsyncIOMotorClient
from sanic import Sanic

from iqplace.helpers import Singleton


class IQPlaceApp(metaclass=Singleton):
    __app_instance = None

    config = None



    def __init__(self, isTest=False):
        app = Sanic()
        self.app = app

        # Load Settings
        settings_module = 'settings.testing' if isTest else os.getenv('SETTINGS_MODULE', 'settings.develop')
        self.config = config = app.config
        config_path = '%s.py' % settings_module.replace('.', '/')
        if isTest:
            config_path = '../../%s' % config_path
        app.config.from_pyfile(config_path)

        self.mongo = app.mongo = AsyncIOMotorClient(config.MONGO_URI)
        self.db_name = config.MONGO_DBNAME
        self.db = app.db = self.mongo[self.db_name]

    def run(self):
        self.app.run(host=self.config.HTTP_HOST, port=self.config.HTTP_PORT, debug=self.config.DEBUG,
                     workers=self.config.HTTP_WORKERS)

    @property
    def test(self):
        return '1'
