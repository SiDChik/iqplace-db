import os
from sanic import Sanic


class IQPlaceApp:
    __app_instance = None

    config = None

    def __new__(cls, *args, **kwargs):
        if not cls.__app_instance:
            cls.__app_instance = super().__new__(cls)

        return cls.__app_instance

    def __init__(self, isTest=False):
        app = Sanic()
        self.app = app

        # Load Settings
        settings_module = 'settings.testing' if isTest else os.getenv('SETTINGS_MODULE', 'settings.default')
        self.config = config = app.config
        app.config.from_pyfile('%s.py' % settings_module.replace('.', '/'))

    def run(self):
        self.app.run(host=self.config.HTTP_HOST, port=self.config.HTTP_PORT, debug=self.config.DEBUG)
