import argparse
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import logging
import select
from utils import get_msg, send_msg
from settings import DEFAULT_SERVER_LISTEN_IP, DEFAULT_SERVER_LISTEN_PORT, ENCODING, MAX_PACKAGE_LENGTH
from log_decorator import log
import logs.config_server_log

SERVER_LOGGER = logging.getLogger('server')


def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', help='Listen port', default=DEFAULT_SERVER_LISTEN_PORT)
    parser.add_argument('--addr', '-a', help='Listen IP', default=DEFAULT_SERVER_LISTEN_IP)
    args = parser.parse_args()
    return args


def server_socket(args):
    server_sock = socket(AF_INET, SOCK_STREAM)
    server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    try:
        server_sock.bind((args.addr, int(args.port)))
        server_sock.settimeout(2)
        server_sock.listen(5)
        SERVER_LOGGER.info(f'Запущен сервер с параметрами адресс: {args.addr}, порт: {args.port}')
    except:
        SERVER_LOGGER.error(f'Не удалось запустить сервер с параметрами адресс: {args.addr}, порт: {args.port}')
    return server_sock


def create_response(message, message_list, client_sock, clients, names):
    if message.get('action') == 'presence':
        if message.get('user') not in names.keys():
            names[message.get('user')] = client_sock
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
        message_list.append(message)
        return
    if message.get('action') == 'exit':
        clients.remove(names[message.get('user')])
        names[message.get('user')].close()
        del names[message.get('user')]
        return
    else:
        response = {
            'response': 400,
            'error': 'Wrong action, try again'
        }
        send_msg(response, client_sock)
        return


def send_message_from_user(message, names, listen_sock):
    if message.get('destination') in names and names[message.get('destination')] in listen_sock:
        send_msg(message, names[message.get('destination')])
        SERVER_LOGGER.info(f"Сообщение {message}, отправлено пользователю {message.get('destination')}")
    else:
        SERVER_LOGGER.error(
            f"Пользователь {message.get('destination')} не зарегистрирован на сервере, отправка сообщения невозможна.")


def main():
    server_sock = server_socket(args_parser())
    clients = []
    messages = []
    names = dict()
    while True:
        try:
            client_sock, addr = server_sock.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'Устанавливаем соединие с клиентом')
            clients.append(client_sock)

        recv_data_lst = []
        send_data_lst = []
        err_list = []
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass
        if recv_data_lst:
            try:
                for client_socket in recv_data_lst:
                    create_response(get_msg(client_socket), messages, client_socket, clients, names)
            except:
                SERVER_LOGGER.info(f'Клиент {client_socket.getpeername()} '
                                   f'отключился от сервера.')
                clients.remove(client_socket)
        for mes in messages:
            try:
                send_message_from_user(mes, names, send_data_lst)
            except Exception:
                SERVER_LOGGER.info(f"Связь с клиентом с именем {mes.get('destination')} была потеряна")
                clients.remove(names[mes.get('destination')])
                del names[mes.get('destination')]
        messages.clear()


if __name__ == '__main__':
    main()