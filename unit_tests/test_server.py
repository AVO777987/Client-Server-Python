import sys
import os
import unittest
import json
from argparse import Namespace
import server
from datetime import datetime

sys.path.append(os.path.join(os.getcwd(), '..'))


class TestClass(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_args_parser(self):
        self.assertEqual(server.args_parser(), Namespace(port=7777, addr=''))

    def test_get_presence_msg(self):
        """Тест работает только когда клиент что то отправляет, а сервер возвращает response"""
        serv_sock = server.server_socket(server.args_parser())
        self.assertEqual(server.send_and_get_msg(serv_sock), {'action': 'error', 'type': 'status',
                                                              'user': {'account_name': 'Client', 'status': 'Hello!'}})


if __name__ == '__main__':
    unittest.main()
