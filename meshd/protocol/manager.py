from abc import abstractmethod
from typing import Dict
from uuid import UUID


class ClosableProtocolConnection:
    @abstractmethod
    def close(self):
        pass


class ProtocolConnectionManager:
    peers: Dict[UUID, ClosableProtocolConnection]

    def __init__(self):
        self.peers = {}

    def __contains__(self, remote_session: UUID):
        return remote_session in self.peers

    def register_connection(self, uuid: UUID, connection: ClosableProtocolConnection):
        self.unregister_connection(uuid)
        self.peers[uuid] = connection

    def unregister_connection(self, uuid: UUID):
        connection = self.peers.pop(uuid, None)
        if connection is not None:
            connection.close()
