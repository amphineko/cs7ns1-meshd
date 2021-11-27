import socket
import struct
from time import sleep
from utils import hash_payload

SENSOR_PORT = 33211

class Transport:
    def __init__(self, protocol, sensor_protocol):
        self.peers = set()
        self.peers_dict = dict() #   peers - Dict of nodes (adr, port)
        self.peers_list = dict() #   peers_list = Dict of a peer's peers
        self.host = socket.gethostbyname(socket.gethostname())
        self.protocol = protocol
        self.sensor_protocol = sensor_protocol

    def update_peers_map(self, session, addr, port, own_protocol_port):
        '''
            Update our peer set based on discovery
        '''
        # print('Discovered session %s from %s:%d' % (session, addr, port))
        new_peer = (addr, port)
        if (new_peer != (self.host, own_protocol_port) and new_peer not in self.peers):
            # TODO : add node id as key
            self.peers.add(new_peer)
            print('Discovered session %s added to peers (%s:%d) \n' % (session, addr, port))
            print('New Peer List', self.peers)

    def read_peer(self):
        '''
            Read protocol packets from the our peers
        '''
        conn, addr = self.protocol.server.accept()
        data = conn.recv(1024)
        # if has hash for data exchange
        data = data.decode('utf-8')
        print("Peer Data recieved: " + str(data) + ' \n')
        conn.close()

    def read_sensor(self):
        '''
            Read protocol packets from the our sensors
        '''
        # data = 'sensor data'
        # self.send_to_peers(data)
        # return None
        #print("Listening for sensor connections on : " + str(ip_addr) + ":" + str(SENSOR_PORT))
        print("Trying to get data from sensor")
        conn, addr = self.sensor_protocol.server.accept()
        data = conn.recv(1024)
        hash, alert_type, payload = struct.unpack('!32si16s', data)
        if hash != hash_payload(payload):
            print("Received packet of wrong hash from sensor")
            return None
        data = struct.unpack('!16s', payload)
        print("Sensor Data recieved: " + str(data) + " with alert_type = " + str(alert_type) + ' \n')
        self.send_to_peers(data)

    def send_to_peers(self, data):
        fail_set = set()
        for p in self.peers:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                print('sending to peer ...', p)
                sock.connect(p)
                sock.send(data.encode())
                sock.close()
            except:
                fail_set.add(p)
        for p in fail_set:
            self.peers.discard(p)
            print('Removed Peer: ' + str(p) + ' \n')

    def close(self):
        self.sock.close()
