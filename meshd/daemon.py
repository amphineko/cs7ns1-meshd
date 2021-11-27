#!/usr/bin/env python3

from threading import Event, Thread
from time import sleep
from uuid import UUID, uuid4
import argparse

from discovery import Discovery
from server import Protocol
from transport import Transport

DISCOVERY_INTERVAL = 3
SENSOR_INTERVAL = 2
PEER_INTERVAL = 1

def read_discovery(discovery, transport, stop: Event):
    '''
    Read discovery packets from the multicast group.
    '''
    while not stop.is_set():
        read_result = discovery.read()
        if read_result is None:
            continue

        session, (addr, port) = read_result
        transport.update_peers_map(session, addr, port, discovery.protocol_port)
        sleep(DISCOVERY_INTERVAL)

def send_discovery(discovery: Discovery, stop: Event):
    '''
    Periodically send discovery packets to the multicast group.
    '''
    while not stop.is_set():
        discovery.send()
        sleep(DISCOVERY_INTERVAL)

def read_sensor(transport: Transport, stop: Event):
    '''
        Read protocol packets from the our sensor (data generation) nodes
    '''
    while not stop.is_set():
        transport.read_sensor()
        sleep(SENSOR_INTERVAL)

def read_peer_sensor(transport: Transport, stop: Event):
    '''
       Read protocol packets from the our peers
    '''
    while not stop.is_set():
        transport.read_peer()
        # sleep(PEER_INTERVAL)

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--sensorport', help='Sensor Port Specification', required=True)
        args = parser.parse_args()

        if args.sensorport is None:
            print("Please specify the type of sensor")
            exit(1)

        sensor_port = int(args.sensorport)

        session = uuid4()
        print('Session %s started \n' % (session))

        protocol = Protocol(None)
        sensor_protocol = Protocol(sensor_port)
        discovery = Discovery(protocol.port, session)
        transport = Transport(protocol, sensor_protocol)

        stop = Event()

        #   Receive Discovery Thread
        discovery_recv_thread = Thread(target=read_discovery, args=(discovery, transport, stop))
        discovery_recv_thread.start()
        #   Send Discovery Thread
        discovery_send_thread = Thread(target=send_discovery, args=(discovery, stop))
        discovery_send_thread.start()
        #   Receive Sensor Data Thread
        peer_sensor_read_thread = Thread(target=read_peer_sensor, args=(transport, stop))
        peer_sensor_read_thread.start()
        #   Send Sensor Data Thread
        sensor_read_thread = Thread(target=read_sensor, args=(transport, stop))
        sensor_read_thread.start()

        discovery_recv_thread.join()
        discovery_send_thread.join()
        peer_sensor_read_thread.join()
        sensor_read_thread.join()

    finally:
        stop.set()

        discovery.close()
        protocol.close()
        # transport.close()
