import socket

class Protocol:
    def __init__(self, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        if (port):
            self.server.bind(('', port))
        else:
            self.server.bind(('', 0))
        self.server.listen()

        _, self.port = self.server.getsockname()

    def close(self):
        self.server.close()
