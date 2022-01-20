import sys
import os
import unittest
import json
from argparse import Namespace
from datetime import datetime
from client import args_parser, send_msg, connect, get_msg, disconnect
sys.path.append(os.path.join(os.getcwd(), '..'))
msg_presence = json.dumps(
    {
        'action': 'presence',
        'time': datetime.now().timestamp(),
        'type': 'status',
        'user': {
            'account_name': 'Client',
            'status': 'Hello!'
        }
    }
)
msg_error = json.dumps(
    {
        'action': 'error',
        'time': datetime.now().timestamp(),
        'type': 'status',
        'user': {
            'account_name': 'Client',
            'status': 'Hello!'
        }
    }
)


class TestClass(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_get_presence_msg(self):
        """ Тест работает только при запущеном сервере """
        client_sock = connect(args_parser())
        send_msg(msg_presence, client_sock)
        self.assertEqual(get_msg(client_sock), {'response': 200, 'msg': 'Hi Client'})
        disconnect(client_sock)

    def test_get_error_msg(self):
        """ Тест работает только при запущеном сервере """
        client_sock = connect(args_parser())
        send_msg(msg_error, client_sock)
        self.assertEqual(get_msg(client_sock), {'response': 400, 'error': 'Wrong action, try again'})
        disconnect(client_sock)

    def test_args_parser(self):
        self.assertEqual(args_parser(), Namespace(port=7777, addr='127.0.0.1'))


if __name__ == '__main__':
    unittest.main()
