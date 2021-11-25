import socket
import random
import struct

from utils import hash_payload

class Sensor:

    # generates intial params on start
    # randomly progresses 'vehicle' down path during each data collection cycle
    # generates other params randomly.

    def __init__(self, sensorType, session, port):
        self.sensorType = sensorType
        self.session = session
        self.port = port

        self.x_pos = random.randint(20,80)
        self.y_pos = random.randint(20,80)
        self.x_lim = 100
        self.y_lim = 100 # defined city block range for travel
        self.journey_len = random.randint(20,50)
        self.pressure = 35
        self.current_step = 0


    def generate_data(self, sensorType):
        metricMap = {'position': self.getPos(),
           'temperature': self.getTemp(),
           'tyre_pressure': self.getPressure(),
           'journey_elapsed': self.getElapsed(),
           'journey_finished': self.getStatus()}


        print('Collecting data from sensor type:', (sensorType))
        if sensorType not in metricMap:
            print('Invalid sensor type found')
            return None
        return metricMap.get(sensorType)

    def send_data(self, data):
        hostname = socket.gethostname()
        print("Hostname : " + socket.gethostbyname(hostname) + " Port : " + self.port)
        print('Sending Data to Sync Node \n')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect_ex((socket.gethostbyname(hostname), int(self.port)))
        data = str(data)
        print("Data : " +  data)
        #hash = hash_payload(bytes(data, 'utf-8'))
        #packet = struct.pack(hash, da
        byte_data = bytes(data, 'utf-8')
        print(byte_data)
        sock.send(byte_data)
        sock.close()

    def getPressure(self):
        self.pressure = self.pressure - random.uniform(0, 0.5)
        return self.pressure

    def getTemp(self):
        return random.uniform(5, 35)

    def getPos(self):
        if self.current_step < self.journey_len:
            self.makeMove()
            self.current_step += 1
        return (self.x_pos, self.y_pos)

    def getElapsed(self):
        return self.current_step

    def getStatus(self):
        if self.current_step < self.journey_len:
            return False
        return True

    def makeMove(self):
        dir = random.randint(1,2) # x or y movement in given move
        move_len =  random.randint(1,3)
        disp = [-1,1][random.randrange(2)] * move_len
        if dir == 1:
            self.y_pos += disp
        else:
            self.x_pos += disp
        self.limitPosition()

    def limitPosition(self): # stay in range
        if self.x_pos > self.x_lim:
            self.x_pos = self.x_lim
        if self.y_pos > self.y_lim:
            self.y_pos = self.y_lim
        if self.x_pos < 0:
            self.x_pos = 0
        if self.y_pos < 0:
            self.y_pos = 0



