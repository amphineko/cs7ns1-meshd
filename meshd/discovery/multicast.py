import socket
import struct
from uuid import UUID

from meshd.utils.sign import hash_payload

MCAST_GROUP = '224.1.1.1'
MCAST_PORT = 33210
MCAST_TTL = 2

SHARED_KEY = b'meshd'


class MulticastDiscovery:
    def __init__(self, protocol_port: int, local_session: UUID, mcast_group=MCAST_GROUP, mcast_port=MCAST_PORT):
        self.protocol_port = protocol_port
        self.session = local_session

        self.group = mcast_group
        self.port = mcast_port

        self.sock = self.create_socket(mcast_group, mcast_port)

    def close(self):
        self.sock.close()

    @staticmethod
    def create_socket(group, port):
        # create udp socket
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP,
        )
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MCAST_TTL)
        sock.bind(('', port))

        # join multicast group
        join_req = struct.pack('=4sl', socket.inet_aton(group), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, join_req)

        return sock

    def read(self, read_timeout=None):
        len_packet = 32 + 16 + 2  # 32 bytes hash, 16 bytes session, 2 bytes port

        # receive packet
        self.sock.settimeout(read_timeout)
        try:
            buf, (remote_addr, remote_port) = self.sock.recvfrom(len_packet)
        except socket.timeout:
            return None
        if len_packet != len(buf):
            print('Received packet of wrong size %d from %s:%d' % (len(buf), remote_addr, remote_port))
            return None

        # verify payload hash against shared key
        payload_hash, payload = struct.unpack('!32s%ds' % (len(buf) - 32), buf)
        if payload_hash != hash_payload(payload):
            print('Received packet of wrong hash from %s:%d' % (remote_addr, remote_port))
            return None

        # decode payload
        _, session, protocol_port = struct.unpack('!32s16sH', buf)
        session = UUID(bytes=session)

        return session, (remote_addr, protocol_port)

    def send(self):
        # encode payload and hash
        payload = struct.pack('!16sH', self.session.bytes, self.protocol_port)
        payload_hash = hash_payload(payload)

        # construct and send packet
        packet = struct.pack('!32s%ds' % len(payload), payload_hash, payload)
        self.sock.sendto(packet, (self.group, self.port))
