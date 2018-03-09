import unittest

from iqplace.app import IQPlaceApp


class TestCase(unittest.TestCase):
    app = None

    def setUp(self):
        self.iqapp = IQPlaceApp(isTest=True)
        self.app = self.iqapp.app
