import unittest

from iqplace.tests.base import TestCase


class ModelsTest(TestCase):
    def test_simple(self):
        print('1')
        self.assertEqual(True, True)