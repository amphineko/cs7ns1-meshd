import socket
import struct
from utils import hash_payload
from time import sleep

DISCOVERY_PORT = 0
SENSOR_PORT = 33211

class Transport:
    def __init__(self):
        self.peers = set()

    def update_peers_set(self, session, addr, port):
        '''
            Update our peer set based on discovery
        '''
        print('Discovered session %s from %s:%d' % (session, addr, port))
        new_peer = (addr, port)
        if (new_peer not in self.peers):
            self.peers.add(new_peer)
            print('Discovered session %s added to peers \n' % (session))
        else:
            print('Discovered session %s already a peer \n' % (session))

    def read_peer(self):
        '''
            Read protocol packets from the our peers
        '''
        return None

    def read_sensor(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostname = socket.gethostname()
        ip_addr = socket.gethostbyname(hostname)
        sock.bind((ip_addr, SENSOR_PORT))
        sock.listen()
        print("Listening for sensor connections on : " + str(ip_addr) + ":" + str(SENSOR_PORT))
        while True:
            print("Trying to get data from sensor")
            conn, addr = sock.accept()
            data = conn.recv(1024)
            print("Data recieved: " + str(data))
            sleep(2)

    def send_to_peers(self, data):
        fail_set = set()
        for p in self.peers:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                sock.connect(p)
                # TODO - Prepare Data
                hash = hash_payload(data)
                packet = struct.pack('!32s%ds' % len(data), hash, data)
                sock.send(packet)
                sock.close()
            except:
                fail_set.add(p)
        for p in fail_set:
            self.peers.discard(p)
            print('Removed Peer: ', p)

    # def close(self):
    #     self.server.close()
