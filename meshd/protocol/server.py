import socket
from threading import Event

ACCEPT_TIMEOUT = 1


class ProtocolServer:
    def __init__(self, accept_timeout: int = ACCEPT_TIMEOUT):
        self.accept_timeout = accept_timeout
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('', 0))
        self.server.listen(1)

        _, self.port = self.server.getsockname()

    def accept_until_stop(self, stop_event: Event):
        self.server.setblocking(False)
        self.server.settimeout(self.accept_timeout)

        while not stop_event.is_set():
            try:
                sock, _ = self.server.accept()
                yield sock
            except socket.timeout:
                pass

    def close(self):
        self.server.close()
