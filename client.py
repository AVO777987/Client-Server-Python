from socket import socket, AF_INET, SOCK_STREAM
import json
from datetime import datetime
import argparse
import logging
import sys
import threading
from time import sleep, time
from settings import DEFAULT_REMOTE_SERVER_IP, DEFAULT_REMOTE_SERVER_PORT, ENCODING, MAX_PACKAGE_LENGTH
from utils import send_msg, get_msg
from metaclasses import ClientVerifier
from client_database import ClientDB
from log_decorator import log
import logs.config_client_log

CLIENT_LOGGER = logging.getLogger('client')

sock_lock = threading.Lock()
database_lock = threading.Lock()

class ClientReader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, client_name, client_sock, database):
        self.client_sock = client_sock
        self.client_name = client_name
        self.database = database
        super().__init__()

    def run(self):
        while True:
            sleep(1)
            with sock_lock:
                try:
                    message = get_msg(self.client_sock)
                except(OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                    CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                else:
                    if message.get("action") == 'message' and message.get('destination') == self.client_name:
                        print(f'\nПолучено сообщение от пользователя {message.get("user")}:'f'\n{message.get("text")}')
                        CLIENT_LOGGER.info(
                            f'Получено сообщение от пользователя {message.get("user")}:\n{message.get("text")}')
                        with database_lock:
                            try:
                                self.database.save_message(message.get("user"), self.client_name, message.get("text"))
                            except Exception as e:
                                print(e)
                                CLIENT_LOGGER.error('Ошибка взаимодействия с базой данных')
                    else:
                        CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')


class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, client_name, client_sock, database):
        self.client_sock = client_sock
        self.client_name = client_name
        self.database = database
        super().__init__()

    def create_messages(self):
        text = input('Введите сообщение для отправки')
        to_user = input('Введите имя пользователя кому вы хотите отправить сообщение ')
        with database_lock:
            try:
                if not self.database.check_user(to_user):
                    CLIENT_LOGGER.error(f'Попытка отправить сообщение незарегистрированому получателю: {to_user}')
                    return
            except Exception as e:
                print(e)
                CLIENT_LOGGER.error('Ошибка взаимодействия с базой данных')
                return

        message = {
            'action': 'message',
            'time': time(),
            'user': self.client_name,
            'destination': to_user,
            'text': text
        }

        with database_lock:
            try:
                self.database.save_message(self.client_name, to_user, message.get('text'))
            except Exception as e:
                print(e)
                CLIENT_LOGGER.error('Ошибка взаимодействия с базой данных')
                return

        with sock_lock:
            try:
                send_msg(message, self.client_sock)
                CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
            except OSError as err:
                if err.errno:
                    CLIENT_LOGGER.error('Потеряно соединение с сервером.')
                    exit(1)
                else:
                    CLIENT_LOGGER.error('Не удалось передать сообщение. Таймаут соединения')

    def create_exit_messages(self):
        message = {
            'action': 'exit',
            'time': time(),
            'user': self.client_name,
        }
        with sock_lock:
            try:
                send_msg(message, self.client_sock)
                CLIENT_LOGGER.info(f'Завершение соединения')
                print('Завершение соединения.')
            except Exception as error:
                CLIENT_LOGGER.error(error)
            sleep(2)
            disconnect(self.client_sock)

    def get_contacts(self):
        with database_lock:
            contacts_list = self.database.get_contacts()
        for contact in contacts_list:
            print(contact)

    def edit_contacts(self):
        command = input('Для удаления введите del, для добавления add: ')
        if command == 'del':
            self.get_contacts()
            contact = input('Введите имя удаляемного контакта: ')
            with database_lock:
                if self.database.check_contact(contact):
                    self.database.del_contact(contact)
                else:
                    CLIENT_LOGGER.error('Такого контакта не существует')
                message = {
                    'action': 'del_contact',
                    'time': time(),
                    'user': self.client_name,
                    'contact': contact
                }
            with sock_lock:
                try:
                    send_msg(message, self.client_sock)
                    answer = get_msg(self.client_sock)
                    if 'response' in answer and answer.get('response') == 200:
                        print(f'Контакт {contact} удален из списка контактов')
                        CLIENT_LOGGER.debug(f'Контакт {contact} удален из списка контактов')
                    else:
                        CLIENT_LOGGER.error('Ошибка удаления контакта')
                except:
                    CLIENT_LOGGER.error('Не удалось отправить информацию на сервер.')
        elif command == 'add':
            contact = input('Введите имя создаваемого контакта: ')
            print(self.database.check_user(contact))
            if self.database.check_user(contact):
                with database_lock:
                    self.database.add_contact(contact)
                message = {
                    'action': 'add_contact',
                    'time': time(),
                    'user': self.client_name,
                    'contact': contact
                }
                with sock_lock:
                    try:
                        send_msg(message, self.client_sock)
                        answer = get_msg(self.client_sock)
                        if 'response' in answer and answer.get('response') == 200:
                            print(f'Контакт {contact} добавлен в список контактов')
                            CLIENT_LOGGER.info(f'Контакт {contact} добавлен в список контактов')
                        else:
                            CLIENT_LOGGER.error('Ошибка добавления контакта')
                    except:
                        CLIENT_LOGGER.error('Не удалось отправить информацию на сервер.')

    def print_history(self):
        command = input('Показать входящие сообщения - in, исходящие - out, все - просто Enter: ')
        with database_lock:
            if command == 'in':
                history_list = self.database.get_history(to_who=self.client_name)
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]} от {message[3]}:\n{message[2]}')
            elif command == 'out':
                history_list = self.database.get_history(from_who=self.client_name)
                for message in history_list:
                    print(f'\nСообщение пользователю: {message[1]} от {message[3]}:\n{message[2]}')
            else:
                history_list = self.database.get_history()
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]}, пользователю {message[1]} '
                          f'от {message[3]}\n{message[2]}')

    @staticmethod
    def print_help():
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('history - история сообщений')
        print('contacts - список контактов')
        print('edit - редактирование списка контактов')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    def run(self):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_messages()
            elif command == 'history':
                self.print_history()
            elif command == 'contacts':
                self.get_contacts()
            elif command == 'edit':
                self.edit_contacts()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                self.create_exit_messages()
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

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


def create_presence(client_name, client_sock):
    CLIENT_LOGGER.debug(f'Отправка приветствия от {client_name}')
    message = {
        'action': 'presence',
        'time': time(),
        'user': client_name,
    }
    send_msg(message, client_sock)
    answer = get_msg(client_sock)
    CLIENT_LOGGER.debug(f'Получен ответ {answer}')
    if 'response' in answer and answer.get('response') == 200:
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    else:
        CLIENT_LOGGER.error('Сервер недосупен')


def get_contacts_list(client_name, client_sock, database):
    CLIENT_LOGGER.debug(f'Запрос контактов пользователя {client_name}')
    message = {
        'action': 'get_contacts',
        'time': time(),
        'user': client_name,
    }
    send_msg(message, client_sock)
    answer = get_msg(client_sock)
    CLIENT_LOGGER.debug(f'Получен ответ {answer}')
    if 'response' in answer and answer.get('response') == 202:
        for contact in answer.get('contact_list'):
            database.add_contact(contact)
    else:
        CLIENT_LOGGER.error(
            f'Не удалось подключиться к серверу,конечный компьютер отверг запрос на подключение.')
        sys.exit(1)


def get_user_list(client_name, client_sock, database):
    CLIENT_LOGGER.debug(f'Запрос списка известных пользователей {client_name}')
    message = {
        'action': 'user_list',
        'time': time(),
        'user': client_name,
    }
    send_msg(message, client_sock)
    answer = get_msg(client_sock)
    CLIENT_LOGGER.debug(f'Получен ответ {answer}')
    if 'response' in answer and answer.get('response') == 200:
        database.add_users(answer.get('user_list'))
    else:
        CLIENT_LOGGER.error('Сервер недосупен')


def main():
    server_address, server_port, client_name = args_parser()
    client_sock = connect(server_address, server_port)

    create_presence(client_name, client_sock)

    database = ClientDB(client_name)
    get_user_list(client_name, client_sock, database)
    get_contacts_list(client_name, client_sock, database)

    receiver = ClientReader(client_name, client_sock, database)
    receiver.daemon = True
    receiver.start()

    user_interface = ClientSender(client_name, client_sock, database)
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
