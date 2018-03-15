import asyncio
import unittest

import uvloop

from iqplace.app import IQPlaceApp

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class TestCase(unittest.TestCase):
    app = None
    loop = None

    def __init__(self, methodName='runTest'):
        self.iqapp = IQPlaceApp(isTest=True)
        self.app = self.iqapp.app
        self.loop = asyncio.get_event_loop()
        self._function_cache = {}
        
        super(TestCase, self).__init__(methodName=methodName)

    def coroutine_function_decorator(self, func):
        def wrapper(*args, **kw):
            return self.loop.run_until_complete(func(*args, **kw))

        return wrapper

    def __getattribute__(self, item):
        attr = object.__getattribute__(self, item)
        if asyncio.iscoroutinefunction(attr):
            if item not in self._function_cache:
                self._function_cache[item] = self.coroutine_function_decorator(attr)
            return self._function_cache[item]
        return attr
