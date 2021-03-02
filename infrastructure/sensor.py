from multiprocessing import Process
import time
import socket
import json
import random
import datetime


class Sensor(Process):
    def __init__(self, port):
        super(Sensor, self).__init__()
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(("127.0.0.1", self.port))

    def run(self):
        while True:
            now = datetime.datetime.now().strftime('%Y%m%dT%H%M')
            payload = random.randrange(0, 100)
            data = {
                'datetime': now,
                'payload': payload 
            }
            self.socket.send(json.dumps(data).encode())
            message = self.socket.recv(4096)
            print('[+] Received: ' + message.decode())
            time.sleep(0.003333333)


#delay for supervisor 
time.sleep(10)


num_sensors = 8
for i in range(num_sensors):
    port = int('800' + str(i))
    sensor = Sensor(port)
    sensor.start()
