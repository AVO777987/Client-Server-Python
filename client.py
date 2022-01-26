from socket import socket, AF_INET, SOCK_STREAM
import json
from datetime import datetime
import argparse
import logging

from settings import DEFAULT_REMOTE_SERVER_IP, DEFAULT_REMOTE_SERVER_PORT, ENCODING, MAX_PACKAGE_LENGTH
from utils import send_msg, get_msg
from log_decorator import log
import logs.config_client_log

CLIENT_LOGGER = logging.getLogger('client')


@log
def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', help='Server port', default=DEFAULT_REMOTE_SERVER_PORT)
    parser.add_argument('--addr', '-a', help='Server IP', default=DEFAULT_REMOTE_SERVER_IP)
    args = parser.parse_args()
    return args


@log
def connect(args):
    client_sock = socket(AF_INET, SOCK_STREAM)
    try:
        client_sock.connect((args.addr, args.port))
        CLIENT_LOGGER.info(f'Запущен клиент с параметрами адресс: {args.addr}, порт: {args.port}')
    except ConnectionRefusedError:
        CLIENT_LOGGER.error(f'Подключение не установлено, т.к. конечный компьютер отверг запрос на подключение')
    return client_sock


@log
def disconnect(client_sock):
    client_sock.close()
    CLIENT_LOGGER.info(f'Клиент разорвал подключение с сервером')


@log
def create_messages(type_msg, user):
    if type_msg == 'presence':
        message = json.dumps(
            {
                'action': 'presence',
                'time': datetime.now().timestamp(),
                'type': 'status',
                'user': user,
                'text': {
                    'status': 'Hello!',
                }
            }
        )
    if type_msg == 'error':
        message = json.dumps(
            {
                'action': 'error',
                'time': datetime.now().timestamp(),
                'type': 'status',
                'user': user,
                'text': {
                    'status': 'Error!'
                }
            }
        )
    return message


def main():
    client_sock = connect(args_parser())
    send_msg(create_messages('presence', 'client'), client_sock)
    data = get_msg(client_sock)
    disconnect(client_sock)
    client_sock = connect(args_parser())
    send_msg(create_messages('error', 'client'), client_sock)
    get_msg(client_sock)
    disconnect(client_sock)


if __name__ == '__main__':
    main()
