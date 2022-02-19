from socket import socket, AF_INET, SOCK_STREAM
import json
from datetime import datetime
import argparse
import logging
import sys
import threading
from time import sleep
from settings import DEFAULT_REMOTE_SERVER_IP, DEFAULT_REMOTE_SERVER_PORT, ENCODING, MAX_PACKAGE_LENGTH
from utils import send_msg, get_msg
from metaclasses import ClientVerifier
from log_decorator import log
import logs.config_client_log

CLIENT_LOGGER = logging.getLogger('client')


def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', help='Server port', default=DEFAULT_REMOTE_SERVER_PORT)
    parser.add_argument('--addr', '-a', help='Server IP', default=DEFAULT_REMOTE_SERVER_IP)
    parser.add_argument('--name', '-n', help='Name Client', default='test33')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name
    return server_address, server_port, client_name


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


def create_messages(type_msg, user):
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
        to_user = input('Введите имя пользователя кому вы хотите отправить сообщение ')
        if text == 'q':
            CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
            sys.exit(0)
        message = {
            'action': 'message',
            'time': datetime.now().timestamp(),
            'type': 'status',
            'user': user,
            'destination': to_user,
            'text': text
        }
    if type_msg == 'exit':
        message = {
            'action': 'exit',
            'time': datetime.now().timestamp(),
            'type': 'status',
            'user': user,
            'text': {
                'status': 'Exit!'
            }
        }
    return message


class ClientReader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, client_sock, client_name):
        self.client_sock = client_sock
        self.client_name = client_name
        super().__init__()

    def run(self):
        while True:
            try:
                message = get_msg(self.client_sock)
                if message.get("action") == 'message' and message.get('destination') == self.client_name:
                    print(f'\nПолучено сообщение от пользователя {message.get("user")}:'
                          f'\n{message.get("text")}')
                    CLIENT_LOGGER.info(
                        f'Получено сообщение от пользователя {message.get("user")}:\n{message.get("text")}')
                else:
                    CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                break


class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, client_sock, client_name):
        self.client_sock = client_sock
        self.client_name = client_name
        super().__init__()

    @staticmethod
    def print_help():
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    def run(self):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                send_msg(create_messages('message', self.client_name), self.client_sock)
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                send_msg(create_messages('exit', self.client_name), self.client_sock)
                print('Завершение соединения.')
                CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
                sleep(2)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')


def main():
    server_address, server_port, client_name = args_parser()
    try:
        client_sock = connect(server_address, server_port)
        send_msg(create_messages('presence', client_name), client_sock)
        data = get_msg(client_sock)
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {data}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.error(
            f'Не удалось подключиться к серверу,конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:
        receiver = ClientReader(client_sock, client_name)
        receiver.daemon = True
        receiver.start()

        user_interface = ClientSender(client_sock, client_name)
        user_interface.daemon = True
        user_interface.start()
        CLIENT_LOGGER.debug('Запущены процессы')

        while True:
            sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
