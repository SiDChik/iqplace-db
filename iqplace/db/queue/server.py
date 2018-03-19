import asyncio
import logging
import signal
from multiprocessing import Lock, Pipe

import sys

from iqplace.helpers import Singleton
import multiprocessing as mp

logger = logging.getLogger('QueueServer')


class QueueServer(metaclass=Singleton):
    app = None

    def __init__(self):
        mp.set_start_method('fork')

    def start_server(self, **server_kwargs):
        def run_server(server):
            server.start(server_kwargs)

        self.process = mp.Process(target=run_server, args=(self,))
        self.process.start()

        def terminate(signum, frame):
            logger.info('Terminate queue server')
            self.process.terminate()

        signal.signal(signal.SIGINT, terminate)

    def terminate(self):
        logger.info('Terminate queue server')
        self.process.terminate()

    def start(self, server_kwargs):
        from iqplace.app import IQPlaceApp

        self.loop = loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        server_kwargs['no_queue'] = True
        self.app = IQPlaceApp(**server_kwargs)

        async def wrapper(server):
            logger.info('Start queue server')
            await server.server_loop()

        try:
            loop.run_until_complete(wrapper(self))
        finally:
            # Завершаем субпроцесс
            sys.exit(1)

    async def server_loop(self):
        class ServerProtocol(asyncio.Protocol):
            transport = None

            def connection_made(self, transport):
                self.transport = transport

            def connection_lost(self, exc):
                self.transport = None

            def data_received(self, data):
                self.transport.write(data)
                self.transport.close()

        coro = self.loop.create_unix_server(ServerProtocol, path='/tmp/queue.sock')
        self.loop.create_task(coro)
        while True:
            await asyncio.sleep(0.1)
