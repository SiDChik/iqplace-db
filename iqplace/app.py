import os
from asyncio import get_event_loop

from motor.motor_asyncio import AsyncIOMotorClient
from sanic import Sanic

from iqplace.db.queue.server import QueueServer
from iqplace.helpers import Singleton


class IQPlaceApp(metaclass=Singleton):
    __app_instance = None

    config = None

    queue = QueueServer()

    def __init__(self, isTest=False, no_queue=False):
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

        from iqplace.auth.urls import auth_blueprint
        self.app.blueprint(auth_blueprint)

        from iqplace.events.urls import events_blueprint
        self.app.blueprint(events_blueprint)

        app.static('/uploads', app.config['UPLOAD_DIR'])

        if not no_queue:
            self.queue.start_server(isTest=isTest)

        pk = open(app.config['SERVER_KEY'], "r")
        self.private_key = pk.read()
        pk.close()

        pk = open(app.config['PUBLIC_KEY'], "r")
        self.public_key = pk.read()
        pk.close()

    def get_collection(self, collection_name):
        collection = self.db[collection_name]
        loop = get_event_loop()
        self.mongo.io_loop = loop
        return collection

    def run(self):
        self.app.run(host=self.config.HTTP_HOST, port=self.config.HTTP_PORT, debug=self.config.DEBUG,
                     workers=self.config.HTTP_WORKERS)

    @property
    def test(self):
        return '1'
