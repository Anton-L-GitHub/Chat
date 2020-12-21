import os
import socket
import pickle
import struct
from threading import Thread


SERVER_IP, PORT = "localhost", 1234


class Client(Thread):

    """ Concerned with opening connecting to server  """

    def __init__(self, *args, **kwargs):
        self.nickname = None
        self.sock = socket.socket()

    def start(self):
        print("Connecting server....\n")
        while True:
            self.sock.connect((SERVER_IP, PORT))

            self.nickname = input("Enter a nickname: ")
            print(f'\nWelcome {self.nickname}!\n\nChat commands:\n- "@exit" to exit,\n- "@list" to list all connected nicknames,\n- "@<friends nickname>" message a specific friend,\n- "@img" to sent picture to server')

            send_thread = Send(self.nickname, self.sock, self).start()
            recevie_thread = Recevie(self.nickname, self.sock, self).start()
            return recevie_thread, send_thread

    def leave(self):
        self.sock.close()
        os._exit(0)


class Send(Thread):

    """ Conserned with sending messages to server """

    def __init__(self, nickname, sock, client):
        super().__init__()
        self.nickname = nickname
        self.sock = sock
        self.client = client

    def run(self):
        self.sock.sendall(self.pack_obj(self.nickname))
        while True:
            try:
                message = input("")
                if message == "@exit":
                    self.client.leave()
                elif message == "@img":
                    self.sock.sendall(self.pack_obj(message))
                    with open("pictures/pic.png", "rb") as file:
                        img = bytes(file.read())
                    self.sock.sendall(self.pack_img(img))
                    print('Image is sent to server!')
                else:
                    self.sock.sendall(self.pack_obj(message))
            except Exception:
                self.client.leave()

    @staticmethod
    def pack_obj(message):
        message_bytes = pickle.dumps(message)
        message_format = f"!L{len(message_bytes)}s"
        message_struct_size = struct.calcsize(message_format)
        message_packed = struct.pack(message_format, message_struct_size, message_bytes)
        return message_packed

    @staticmethod
    def pack_img(img):
        img_format = f"!L{len(img)}s"
        img_struct_size = struct.calcsize(img_format)
        img_pack = struct.pack(img_format, img_struct_size, img)
        return img_pack


class Recevie(Thread):

    """ Thread conserned with listening and receving messages from server """

    def __init__(self, nickname, sock, client):
        super().__init__()
        self.nickname = nickname
        self.sock = sock
        self.client = client

    def run(self):
        while True:
            try:
                message = self.unpack_obj()
                if message:
                    print(message)
                else:
                    print("Error, try to reconnect!")
                    self.close()
                    break

            except ConnectionResetError:
                print("Server went offline... Try to reconnect")
                self.client.leave()

    def unpack_obj(self):
        header = self.sock.recv(4)
        (message_length,) = struct.unpack("!L", header)
        message_length = int(message_length - 4)
        message = self.sock.recv(message_length)
        message = pickle.loads(message)
        return message


if __name__ == "__main__":
    server = Client()
    server.start()
