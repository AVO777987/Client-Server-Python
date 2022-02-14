import argparse
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import logging
import select
from utils import get_msg, send_msg
from settings import DEFAULT_SERVER_LISTEN_IP, DEFAULT_SERVER_LISTEN_PORT, ENCODING, MAX_PACKAGE_LENGTH
from metaclasses import ServerVerifier
from descrptrs import Port
from log_decorator import log
import logs.config_server_log

SERVER_LOGGER = logging.getLogger('server')


def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', help='Listen port', default=DEFAULT_SERVER_LISTEN_PORT)
    parser.add_argument('--addr', '-a', help='Listen IP', default=DEFAULT_SERVER_LISTEN_IP)
    args = parser.parse_args()
    listen_address = args.addr
    listen_port = args.port
    return listen_address, listen_port


class Server(metaclass=ServerVerifier):
    listen_port = Port()

    def __init__(self, listen_address, listen_port):
        self.listen_address = listen_address
        self.listen_port = 7777
        self.clients = []
        self.message_list = []
        self.names = dict()

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
                try:
                    for client_socket in recv_data_lst:
                        self.create_response(get_msg(client_socket), client_socket)
                except:
                    SERVER_LOGGER.info(f'Клиент {client_socket.getpeername()} '
                                       f'отключился от сервера.')
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
        if message.get('action') == 'presence':
            if message.get('user') not in self.names.keys():
                self.names[message.get('user')] = client_sock
                response = {
                    'response': 200,
                    'msg': f'Hi {message.get("user")}'
                }
                send_msg(response, client_sock)
            else:
                response = {
                    'response': 400,
                    'msg': f'Имя {message.get("user")} уже занято.'
                }
                send_msg(response, client_sock)
            return
        if message.get('action') == 'message':
            self.message_list.append(message)
            return
        if message.get('action') == 'exit':
            self.clients.remove(self.names[message.get('user')])
            self.names[message.get('user')].close()
            del self.names[message.get('user')]
            return
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


def main():
    listen_address, listen_port = args_parser()
    # Создание экземпляра класса - сервера.
    server = Server(listen_address, listen_port)
    server.run()


if __name__ == '__main__':
    main()
