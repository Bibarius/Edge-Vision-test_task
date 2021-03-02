import asyncio
from aiohttp import web
import json
import socket
import datetime

class SensorHandler(asyncio.Protocol):

    def __init__(self, snum, system_state):
        super(SensorHandler, self).__init__()
        self.sensor_number = snum
        self.system_state = system_state

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {} on port'.format(peername))
        self.transport = transport

    def data_received(self, data):
        message = json.loads(data.decode())
        payload = message['payload']
        self.system_state[self.sensor_number] = payload

        print('Send: {!r}'.format(message))
        self.transport.write(data)



class Controller():
    def __init__(self, num_sensors):
        self.system_state = [0 for _ in range(num_sensors)]
        self.last_descision = {}
        
        '''manipulator connection'''
        self.manipulator_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.manipulator_connection.connect(("127.0.0.1", 7000))

    def run(self):
        sensors_numbers = [0, 1, 2, 3, 4, 5, 6, 7]
        asyncio.run(self.init_sensors_handlers(sensors_numbers))

    async def manipulate(self):
        """Решение об управляющем сигнале "перевести манипулятор в положение up" принимается,
                если большая часть (> 4) текущих значений сенсоров больше 50. 
                В ином случае принимается решение перевести манипулятор в положение "down".
            """

        while True:
            await asyncio.sleep(5)
            now = datetime.datetime.now().strftime('%Y%m%dT%H%M')
            message = {
                'datetime': now
            } 
            if len(list(filter(lambda x: x > 50, self.system_state))) > 4:
                message['status'] = 'up'
            else:
                message['status'] = 'down'
            self.manipulator_connection.send(json.dumps(message).encode())
            message['time_of_decision'] = now
            self.last_descision = message

            # message = self.socket.recv(4096)

    async def server(self):
        app = web.Application()
        app.add_routes([web.get('/', self.handle)])
        handler = app.make_handler()
        loop = asyncio.get_running_loop()
        server = await loop.create_server(handler, '0.0.0.0', 8080)
        await server.serve_forever()


    async def init_handler(self, number):
        port = int('800' + str(number))
        loop = asyncio.get_running_loop()
        server = await loop.create_server(lambda: SensorHandler(number, self.system_state), '127.0.0.1', port)
        await server.serve_forever()

    async def init_sensors_handlers(self, snumbers: list):
        coroutines = [self.init_handler(n) for n in snumbers]
        coroutines.append(self.server())
        coroutines.append(self.manipulate())
        await asyncio.gather(*coroutines)


    async def handle(self, request):
        message = self.last_descision
        message['datetime'] = datetime.datetime.now().strftime('%Y%m%dT%H%M')
        data = str(json.dumps(message))
        return web.Response(text=data)




controller = Controller(8)
controller.run()

