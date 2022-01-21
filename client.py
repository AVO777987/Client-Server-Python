from socket import socket, AF_INET, SOCK_STREAM
import json
from datetime import datetime
import argparse
from settings import DEFAULT_REMOTE_SERVER_IP, DEFAULT_REMOTE_SERVER_PORT, ENCODING, MAX_PACKAGE_LENGTH
import logging
import logs.config_client_log

CLIENT_LOGGER = logging.getLogger('client')


def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', help='Server port', default=DEFAULT_REMOTE_SERVER_PORT)
    parser.add_argument('--addr', '-a', help='Server IP', default=DEFAULT_REMOTE_SERVER_IP)
    args = parser.parse_args()
    return args


def connect(args):
    client_sock = socket(AF_INET, SOCK_STREAM)
    try:
        client_sock.connect((args.addr, args.port))
        CLIENT_LOGGER.info(f'Запущен клиент с параметрами адресс: {args.addr}, порт: {args.port}')
    except ConnectionRefusedError:
        CLIENT_LOGGER.error(f'Подключение не установлено, т.к. конечный компьютер отверг запрос на подключение')
    return client_sock


def send_msg(msg, client_sock):
    try:
        client_sock.send(msg.encode(ENCODING))
        CLIENT_LOGGER.debug(f'Отправлено сообщение на сервер: {msg}')
    except AttributeError:
        CLIENT_LOGGER.error(f'Попытка отправить не JSON')
    except:
        CLIENT_LOGGER.error(f'Не удалось отправить сообщение на сервер!')


def get_msg(client_sock):
    try:
        data = json.loads(client_sock.recv(MAX_PACKAGE_LENGTH).decode('utf-8'))
        CLIENT_LOGGER.debug(f'Получено сообщение с сервера: {data}')
        if data.get('response') == 200:
            print(
                f'Response Message: {data.get("msg")}'
            )
        else:
            print(
                f'Error: {data.get("error")}'
            )
    except OSError:
        CLIENT_LOGGER.error('Запрос на отправку или получение данных  (when sending on a datagram '
                            'socket using a sendto call) no address was supplied')


def disconnect(client_sock):
    client_sock.close()
    CLIENT_LOGGER.info(f'Клиент разорвал подключение с сервером')


if __name__ == '__main__':
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

    msg_no_json = {}

    args = args_parser()
    client_sock = connect(args)
    send_msg(msg_error, client_sock)
    get_msg(client_sock)
    disconnect(client_sock)
    client_sock = connect(args)
    send_msg(msg_presence, client_sock)
    get_msg(client_sock)
    disconnect(client_sock)
    client_sock = connect(args)
    send_msg(msg_no_json, client_sock)
    get_msg(client_sock)
    disconnect(client_sock)
