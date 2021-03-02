import asyncio
import logging
import json

class Manipulator(asyncio.Protocol):

    def __init__(self):
        super(Manipulator, self).__init__()
        self.init_logging()
        self.state = 'down'

    @staticmethod
    def init_logging():
        logging.basicConfig(filename='manipulator.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


    def on_event(self, state):
        self.state = state if self.state != state else self.state

    def log(self):
        logging.info(self.state)

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        print('Data received: {!r}'.format(message))
        data = json.loads(message)
        self.on_event(data['status'])
        self.log()

        print('Send: {!r}'.format(message))
        self.transport.write(message.encode())


async def main():
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: Manipulator(),
        '127.0.0.1', 7000)

    async with server:
        await server.serve_forever()


asyncio.run(main())

