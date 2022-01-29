from socket import socket, AF_INET, SOCK_STREAM
import json
from datetime import datetime
import argparse
import logging
import sys
from time import sleep

from settings import DEFAULT_REMOTE_SERVER_IP, DEFAULT_REMOTE_SERVER_PORT, ENCODING, MAX_PACKAGE_LENGTH
from utils import send_msg, get_msg
from log_decorator import log
import logs.config_client_log

CLIENT_LOGGER = logging.getLogger('client')


def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', help='Server port', default=DEFAULT_REMOTE_SERVER_PORT)
    parser.add_argument('--addr', '-a', help='Server IP', default=DEFAULT_REMOTE_SERVER_IP)
    parser.add_argument('--mode', '-m', help='Client Mod', default='send')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode
    return server_address, server_port, client_mode


def connect(server_address, server_port):
    client_sock = socket(AF_INET, SOCK_STREAM)
    try:
        client_sock.connect((server_address, server_port))
        CLIENT_LOGGER.info(f'Запущен клиент с параметрами адресс: {server_address}, порт: {server_port}')
    except ConnectionRefusedError:
        CLIENT_LOGGER.error(f'Подключение не установлено, т.к. конечный компьютер отверг запрос на подключение')
    return client_sock


def disconnect(client_sock):
    client_sock.close()
    CLIENT_LOGGER.info(f'Клиент разорвал подключение с сервером')


def create_messages(type_msg, user='Guest'):
    if type_msg == 'presence':
        message = {
            'action': 'presence',
            'time': datetime.now().timestamp(),
            'type': 'status',
            'user': user,
            'text': {
                'status': 'Hello!',
            }
        }
    if type_msg == 'message':
        text = input('Введите сообщение для отправки или q для завершения работы: ')
        if text == 'q':
            CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
            sys.exit(0)
        message = {
            'action': 'message',
            'time': datetime.now().timestamp(),
            'type': 'status',
            'user': user,
            'text': text
        }
    if type_msg == 'error':
        message = {
            'action': 'error',
            'time': datetime.now().timestamp(),
            'type': 'status',
            'user': user,
            'text': {
                'status': 'Error!'
            }
        }
    return message


def main():
    server_address, server_port, client_mode = args_parser()
    try:
        client_sock = connect(server_address, server_port)
        send_msg(create_messages('presence', 'client'), client_sock)
        data = get_msg(client_sock)
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {data}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(
            f'Не удалось подключиться к серверу,конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:
        if client_mode == 'send':
            print('Режим работы - отправка сообщений.')
        else:
            print('Режим работы - приём сообщений.')
        while True:
            sleep(2)
            if client_mode == 'send':
                try:
                    send_msg(create_messages('message'), client_sock)
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)

            if client_mode == 'listen':
                try:
                    print(get_msg(client_sock))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)


if __name__ == '__main__':
    main()
