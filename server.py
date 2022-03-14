import argparse
import configparser
import os
import sys
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import logging
import select
from utils import get_msg, send_msg
from settings import DEFAULT_SERVER_LISTEN_IP, DEFAULT_SERVER_LISTEN_PORT, ENCODING, MAX_PACKAGE_LENGTH
import threading
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from server_gui import MainWindow, gui_create_model, HistoryWindow, create_stat_model, ConfigWindow
from metaclasses import ServerVerifier
from descrptrs import Port
from server_database import ServerDB
from log_decorator import log
import logs.config_server_log

SERVER_LOGGER = logging.getLogger('server')
new_connection = False
conflag_lock = threading.Lock()


def args_parser(default_port, default_address):
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', help='Listen port', default=default_port)
    parser.add_argument('--addr', '-a', help='Listen IP', default=default_address)
    args = parser.parse_args()
    listen_address = args.addr
    listen_port = args.port
    return listen_port, listen_address


class Server(threading.Thread, metaclass=ServerVerifier):
    listen_port = Port()

    def __init__(self, listen_address, listen_port, database):
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.database = database
        self.clients = []
        self.message_list = []
        self.names = dict()
        super().__init__()

    def server_socket(self):
        server_sock = socket(AF_INET, SOCK_STREAM)
        server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        try:
            server_sock.bind((self.listen_address, self.listen_port))
            server_sock.settimeout(2)
            server_sock.listen(5)
            SERVER_LOGGER.info(f'Запущен сервер с параметрами адресс: {self.listen_address}, порт: {self.listen_port}')
        except:
            SERVER_LOGGER.error(f'Не удалось запустить сервер с параметрами адресс: {self.listen_address}, '
                                f'порт: {self.listen_port}')
        return server_sock

    def run(self):
        server_sock = self.server_socket()
        while True:
            try:
                client_sock, addr = server_sock.accept()
            except OSError:
                pass
            else:
                SERVER_LOGGER.info(f'Устанавливаем соединие с клиентом')
                self.clients.append(client_sock)

            recv_data_lst = []
            send_data_lst = []
            err_list = []
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass
            if recv_data_lst:
                for client_socket in recv_data_lst:
                    try:
                        self.create_response(get_msg(client_socket), client_socket)
                    except:
                        SERVER_LOGGER.info(f'Клиент {client_socket.getpeername()} '
                                           f'отключился от сервера.')
                        for name in self.names:
                            if self.names[name] == client_socket:
                                self.database.user_logout(name)
                                del self.names[name]
                                break
                        self.clients.remove(client_socket)
            for mes in self.message_list:
                try:
                    self.send_message_from_user(mes, send_data_lst)
                except Exception as error:
                    print(error)
                    SERVER_LOGGER.info(f"Связь с клиентом с именем {mes.get('destination')} была потеряна")
                    self.clients.remove(self.names[mes.get('destination')])
                    del self.names[mes.get('destination')]
            self.message_list.clear()

    def create_response(self, message, client_sock):
        global new_connection
        if message.get('action') == 'presence':
            if message.get('user') not in self.names.keys():
                self.names[message.get('user')] = client_sock
                response = {
                    'response': 200,
                    'msg': f'Hi {message.get("user")}'
                }
                client_ip, client_port = client_sock.getpeername()
                self.database.user_login(message.get('user'), client_ip, client_port)
                send_msg(response, client_sock)
                with conflag_lock:
                    new_connection = True
            else:
                response = {
                    'response': 400,
                    'msg': f'Имя {message.get("user")} уже занято.'
                }
                send_msg(response, client_sock)
            return
        elif message.get('action') == 'message':
            self.message_list.append(message)
            self.database.process_message(
                message.get('user'), message.get('destination'))
            return
        elif message.get('action') == 'exit':
            self.database.user_logout(message.get('user'))
            self.clients.remove(self.names[message.get('user')])
            self.names[message.get('user')].close()
            del self.names[message.get('user')]
            with conflag_lock:
                new_connection = True
            return
        elif message.get('action') == 'get_contacts':
            contact_list = self.database.get_contacts(message.get('user'))
            response = {
                'response': 202,
                'contact_list': contact_list
            }
            send_msg(response, client_sock)
        elif message.get('action') == 'add_contact':
            self.database.add_contact(message.get('user'), message.get('contact'))
            response = {
                'response': 200,
            }
            send_msg(response, client_sock)
        elif message.get('action') == 'del_contact':
            self.database.remove_contact(message.get('user'), message.get('contact'))
            response = {
                'response': 200,
            }
            send_msg(response, client_sock)
        elif message.get('action') == 'user_list':
            user_list = [user[0] for user in self.database.users_list()]
            response = {
                'response': 200,
                'user_list': user_list,
            }
            send_msg(response, client_sock)
        else:
            response = {
                'response': 400,
                'error': 'Wrong action, try again'
            }
            send_msg(response, client_sock)
            return

    def send_message_from_user(self, message, listen_sock):
        if message.get('destination') in self.names and self.names[message.get('destination')] in listen_sock:
            send_msg(message, self.names[message.get('destination')])
            SERVER_LOGGER.info(f"Сообщение {message}, отправлено пользователю {message.get('destination')}")
        else:
            SERVER_LOGGER.error(
                f"Пользователь {message.get('destination')} не зарегистрирован на сервере, отправка сообщения невозможна.")


def print_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключённых пользователей')
    print('loghist - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')


def main():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")
    listen_port, listen_address = args_parser(
        config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])
    # listen_address, listen_port = args_parser()
    listen_port = int(listen_port)
    database = ServerDB(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))
    # database = ServerDB()
    print(os.path.join(config['SETTINGS']['Database_path'], config['SETTINGS']['Database_file']))
    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    # Создаём графическое окружение для сервера:
    server_app = QApplication(sys.argv)
    main_window = MainWindow()

    # Инициализируем параметры в окна
    main_window.statusBar().showMessage('Server Working')
    main_window.active_clients_table.setModel(gui_create_model(database))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()

    # Функция, обновляющая список подключённых, проверяет флаг подключения, и
    # если надо обновляет список
    def list_update():
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(
                gui_create_model(database))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    # Функция, создающая окно со статистикой клиентов
    def show_statistics():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(database))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        stat_window.show()

    # Функция создающяя окно с настройками сервера.
    def server_config():
        global config_window
        # Создаём окно и заносим в него текущие параметры
        config_window = ConfigWindow()
        config_window.db_path.insert(config['SETTINGS']['Database_path'])
        config_window.db_file.insert(config['SETTINGS']['Database_file'])
        config_window.port.insert(config['SETTINGS']['Default_port'])
        config_window.ip.insert(config['SETTINGS']['Listen_Address'])
        config_window.save_btn.clicked.connect(save_server_config)

    # Функция сохранения настроек
    def save_server_config():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['Database_path'] = config_window.db_path.text()
        config['SETTINGS']['Database_file'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            config['SETTINGS']['Listen_Address'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['Default_port'] = str(port)
                print(port)
                with open('server.ini', 'w') as conf:
                    config.write(conf)
                    message.information(
                        config_window, 'OK', 'Настройки успешно сохранены!')
            else:
                message.warning(
                    config_window,
                    'Ошибка',
                    'Порт должен быть от 1024 до 65536')

    # Таймер, обновляющий список клиентов 1 раз в секунду
    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    # Связываем кнопки с процедурами
    main_window.refresh_button.triggered.connect(list_update)
    main_window.show_history_button.triggered.connect(show_statistics)
    main_window.config_btn.triggered.connect(server_config)

    # Запускаем GUI
    server_app.exec_()


if __name__ == '__main__':
    main()
