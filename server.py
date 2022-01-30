import argparse
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import json
import logging
import select
from datetime import datetime
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


def create_response(message, message_list, client_sock):
    if message.get('action') == 'presence':
        response = {
            'response': 200,
            'msg': f'Hi {message.get("user")}'
        }
        send_msg(response, client_sock)
        return
    if message.get('action') == 'message':
        message_list.append((message.get('user'), message.get('text')))
        return
    else:
        response = {
            'response': 400,
            'error': 'Wrong action, try again'
        }
        send_msg(response, client_sock)
        return


def disconect(serv_sock):
    serv_sock.close()


def main():
    server_sock = server_socket(args_parser())
    clients = []
    messages = []
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
                    create_response(get_msg(client_socket), messages, client_socket)
            except:
                SERVER_LOGGER.info(f'Клиент {client_socket.getpeername()} '
                                   f'отключился от сервера.')
                clients.remove(client_socket)
        if messages and send_data_lst:
            message = {
                'action': 'message',
                'time': datetime.now().timestamp(),
                'sender': messages[0][0],
                'text': messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data_lst:
                try:
                    send_msg(message, waiting_client)
                except:
                    SERVER_LOGGER.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                    waiting_client.close()
                    clients.remove(waiting_client)


if __name__ == '__main__':
    main()
