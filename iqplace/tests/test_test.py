import asyncio
import unittest

from iqplace.tests.base import TestCase


class TestTest(TestCase):
    def test_simple(self):
        print('1')
        self.assertEqual(True, True)

    async def test_async(self):
        print('wait 500ms')
        await asyncio.sleep(0.5)
        print('done')
        self.assertEqual(True, True)