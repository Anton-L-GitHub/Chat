import pickle
import socket
import struct
from threading import Thread


HOST_IP, HOST_PORT = "localhost", 1234


class Server(Thread):

    """ Concerned with accepting new connections and functions for the server """

    def __init__(self, host_ip=HOST_IP, host_port=HOST_PORT, *args, **kwargs):
        super().__init__()
        self.active_connections = []
        self.sock = socket.socket()
        self.sock.bind((host_ip, host_port))
        self.sock.listen()

    def run(self):
        print("[SERVER HAS STARTED]")

        while True:
            client_socket, client_addr = self.sock.accept()

            connection = Connection(client_socket, client_addr, self)
            self.active_connections.append(connection)
            print(f"[NEW CONNNECTION] - {client_addr}")
            connection.start()

    def remove_connection(self, connection):
        self.active_connections.remove(connection)

    def message_all(self, message, connection):
        """Takes unpacked message, sends packed message to all active connections"""
        for person in self.active_connections:
            if person != connection:
                person.sock.sendall(self.pack_obj(message))

    def special_function(self, message, command, connection):
        for connection in self.active_connections:
            if command == connection.nickname:
                self.message_friend(message, command, connection)
                return

        if command == "list":
            message = self.pack_obj((f"Online: {str(self.list_nicknames)}"))
            connection.sock.sendall(message)

        else:
            message = self.pack_obj((f"Invalid command, try again!"))
            connection.sock.sendall(message)

    def message_friend(self, message, friend, conncetion):
        for client in self.active_connections:
            if client.nickname == friend:
                message = f'-DIRECT MESSAGE FROM "{conncetion.nickname}": {message[len(friend) + 2:]}'
                print(f"{conncetion.nickname} -> {message}")
                client.sock.sendall(self.pack_obj(message))

    @staticmethod
    def pack_obj(message):
        message_bytes = pickle.dumps(message)
        message_format = f"!L{len(message_bytes)}s"
        message_struct_size = struct.calcsize(message_format)
        message_packed = struct.pack(message_format, message_struct_size, message_bytes)
        return message_packed

    @property
    def list_nicknames(self):
        """ Returns list of nicknames of all connected clients """
        return ", ".join(
            [connection.nickname for connection in self.active_connections]
        )


class Connection(Thread):

    """ Concerned with serving a connection  """

    def __init__(self, client_sock, client_addr, server):
        super().__init__()
        self.server = server
        self.sock = client_sock
        self.address = client_addr
        self.nickname = None

    def run(self):
        try:
            self.nickname = self.unpack_obj()
            self.server.message_all(f'"{self.nickname}" has joined the party!', self)

            while True:
                message = self.unpack_obj()
                if message:
                    if message[0] == "@":
                        command = message.split()[0][1:]
                        if command == "img":
                            image = self.unpack_img()
                            with open("received_img.png", "wb") as file:
                                file.write(image)
                        else:
                            self.server.special_function(message, command, self)
                    else:
                        message = f"{self.nickname}: {message}"
                        print(f"{self.address[0]} - {message}")
                        self.server.message_all(message, self)

        except ConnectionResetError or OSError:
            self.leave()

    def leave(self):
        print(f"{self.address} - {self.nickname} has left")
        self.server.message_all(f'"{self.nickname}" has left the party!', self)
        self.server.active_connections.remove(self)
        self.sock.close()

    def unpack_obj(self):
        header = self.sock.recv(4)
        (message_length,) = struct.unpack("!L", header)
        message_length = int(message_length - 4)
        message = self.sock.recv(message_length)
        message = pickle.loads(message)
        return message

    def unpack_img(self):
        header = self.sock.recv(4)
        (message_length,) = struct.unpack("!L", header)
        message_length = int(message_length - 4)
        message = self.sock.recv(message_length)
        return message


if __name__ == "__main__":
    server = Server()
    server.start()
