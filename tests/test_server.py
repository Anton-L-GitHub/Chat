from server import Connection, Server
from unittest import TestCase, main
from unittest.mock import MagicMock, call, patch


class TestHappyServer(TestCase):
    @patch("server.socket")
    def setUp(self, mock_socket):
        self.server = Server(daemon=True)
        self.server.sock = mock_socket

    def test_init(self):
        self.assertIsInstance(self.server, Server)
        self.assertEqual(len(self.server.active_connections), 0)
        self.assertFalse(self.server.is_alive())

    def test_remove_connection(self):
        connection = MagicMock()
        self.server.active_connections.append(connection)
        self.assertEqual(len(self.server.active_connections), 1)

        self.server.remove_connection(connection)
        self.assertEqual(len(self.server.active_connections), 0)

    def test_message_all(self):
        person1 = MagicMock()
        person2 = MagicMock()
        person3 = MagicMock()
        self.server.active_connections = [person1, person2, person3]

        self.server.message_all("Test", person1)
        person1.sock.sendall.assert_not_called()
        person2.sock.sendall.assert_called_once_with(Server.pack_obj("Test"))
        person3.sock.sendall.assert_called_once_with(Server.pack_obj("Test"))

    @patch("builtins.print")
    def test_message_friend(self, mock_print):
        person1 = MagicMock()
        person2 = MagicMock()
        person1.nickname = "Person1"
        person2.nickname = "Person2"
        self.server.active_connections = [person1, person2]
        message = "@Person1 Testmsg"
        self.server.message_friend(message, person2.nickname, person1)

        mock_print.assert_called_once_with(
            'Person1 -> -DIRECT MESSAGE FROM "Person1": Testmsg'
        )
        person1.sock.sendall.assert_not_called()
        person2.sock.sendall.assert_called_once_with(
            self.server.pack_obj(f'-DIRECT MESSAGE FROM "Person1": Testmsg')
        )

    def test_pack_obj_list(self):
        obj = ["Hejsan allihop", "Hur är läget?"]
        expected_result = b"\x00\x00\x007\x80\x04\x95(\x00\x00\x00\x00\x00\x00\x00]\x94(\x8c\x0eHejsan allihop\x94\x8c\x0fHur \xc3\xa4r l\xc3\xa4get?\x94e."

        result = self.server.pack_obj(obj)

        self.assertEqual(expected_result, result)

    def test_Server_pack_obj_dict(self):
        obj = {"Hej": "Hello", "Hur": "How"}
        expected_result = b"\x00\x00\x00.\x80\x04\x95\x1f\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x03Hej\x94\x8c\x05Hello\x94\x8c\x03Hur\x94\x8c\x03How\x94u."

        result = self.server.pack_obj(obj)

        self.assertEqual(expected_result, result)

    def test_Server_pack_tuple(self):
        obj = ("Hejsan", "Hur")
        expected_result = b"\x00\x00\x00!\x80\x04\x95\x12\x00\x00\x00\x00\x00\x00\x00\x8c\x06Hejsan\x94\x8c\x03Hur\x94\x86\x94."

        result = self.server.pack_obj(obj)

        self.assertEqual(expected_result, result)

    def test_Server_pack_list_of_dict(self):
        obj = [{"Hej": "Hello", "Hur": "How"}, {"Hej": "Hello", "Hur": "How"}]
        expected_result = b"\x00\x00\x00>\x80\x04\x95/\x00\x00\x00\x00\x00\x00\x00]\x94(}\x94(\x8c\x03Hej\x94\x8c\x05Hello\x94\x8c\x03Hur\x94\x8c\x03How\x94u}\x94(h\x02h\x03h\x04h\x05ue."

        result = self.server.pack_obj(obj)

        self.assertEqual(expected_result, result)

    def test_Server_pack_obj_str_returns_bytes(self):
        result = self.server.pack_obj("test_str")

        self.assertIsInstance(result, bytes)

    def test_nicknames(self):
        person1 = MagicMock()
        person2 = MagicMock()
        person1.nickname = "Nickname1"
        person2.nickname = "Nickname2"
        self.server.active_connections = [person1, person2]

        nicknames_online = self.server.list_nicknames
        self.assertEqual(nicknames_online, "Nickname1, Nickname2")


class TestHappyConnection(TestCase):
    def setUp(self):
        self.client_sock = MagicMock()
        self.client_addr = MagicMock()
        self.client_server = MagicMock()
        self.connection = Connection(
            self.client_sock, self.client_sock, self.client_server
        )

    def test_init(self):
        self.assertIsInstance(self.connection, Connection)
        self.assertFalse(self.connection.is_alive())
        self.assertFalse(self.connection.nickname)

    # @patch('server.message_all')
    # def test_leave(self):
    #     self.connection.leave()

    # def test_unpack_obj(self):
    #     self.connection.sock.recv = MagicMock()
    #     self.connection.sock.recv.return_value = b'\x00\x00\x00\x17'
    #     self.connection.sock.recv.return_value = b'\x80\x04\x95\x08\x00\x00\x00\x00\x00\x00\x00\x8c\x04test\x94.'
    #     self.connection.unpack_obj()


if __name__ == "__main__":
    main()
