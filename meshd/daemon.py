#!/usr/bin/env python3

from threading import Event, Thread
from uuid import uuid4, UUID

from discovery.multicast import MulticastDiscovery
from meshd.protocol.connection import ProtocolConnection
from meshd.protocol.manager import ProtocolConnectionManager
from protocol.server import ProtocolServer

DISCOVERY_INTERVAL = 1


def discovery_main(discovery: MulticastDiscovery,
                   local_session: UUID,
                   protocol_manager: ProtocolConnectionManager,
                   stop_event: Event):
    cache = {}

    while not stop_event.is_set():
        result = discovery.read(DISCOVERY_INTERVAL)
        if result:
            remote_session, (remote_addr, remote_port) = result

            if (remote_addr, remote_port) in cache:
                continue
            cache[(remote_addr, remote_port)] = True

            if remote_session < local_session and remote_session not in protocol_manager:
                ProtocolConnection.connect(local_session, remote_addr, remote_port, stop_event)

        discovery.send()


def protocol_main(local_session: UUID, manager: ProtocolConnectionManager, server: ProtocolServer, stop_event: Event):
    cache = {}

    for sock in server.accept_until_stop(stop_event):
        remote_addr, remote_port = sock.getpeername()

        if (remote_addr, remote_port) in cache:
            continue
        cache[(remote_addr, remote_port)] = True

        ProtocolConnection.accept(local_session, sock, stop_event)


def main():
    session = uuid4()  # local session id
    stop = Event()  # root cancellation event

    try:
        protocol_server = ProtocolServer()
        protocol_manager = ProtocolConnectionManager()
        discovery = MulticastDiscovery(protocol_server.port, session)

        discovery_thread = Thread(target=discovery_main, args=(discovery, session, protocol_manager, stop))
        discovery_thread.start()

        protocol_accept_thread = Thread(target=protocol_main, args=(session, protocol_manager, protocol_server, stop))
        protocol_accept_thread.start()

        print(f"Local session {session} started")

        discovery_thread.join()
        protocol_accept_thread.join()
    finally:
        stop.set()


if __name__ == '__main__':
    main()
