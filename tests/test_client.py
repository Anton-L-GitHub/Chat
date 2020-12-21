from client import Client
from unittest import TestCase, main
from unittest.mock import MagicMock, patch


class TestHappyClient(TestCase):
    @patch("client.socket")
    def setUp(self, mock_socket):
        self.client = Client()
        self.client.sock = mock_socket

    def test_Client_init(self):
        self.assertIsInstance(self.client, Client)
        self.assertIsInstance(self.client.sock, MagicMock)
        self.assertIsNone(self.client.nickname)
        self.client.nickname = "Göran"
        self.assertEqual(self.client.nickname, "Göran")


if __name__ == "__main__":
    main()
