import argparse
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import json
from settings import DEFAULT_SERVER_LISTEN_IP, DEFAULT_SERVER_LISTEN_PORT, ENCODING, MAX_PACKAGE_LENGTH
import logging
import logs.config_server_log

SERVER_LOGGER = logging.getLogger('server')

def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', help='Listen port', default=DEFAULT_SERVER_LISTEN_PORT)
    parser.add_argument('--addr', '-a', help='Listen IP', default=DEFAULT_SERVER_LISTEN_IP)
    args = parser.parse_args()
    return args


def server_socket(args):
    serv_sock = socket(AF_INET, SOCK_STREAM)
    serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    try:
        serv_sock.bind((args.addr, int(args.port)))
        serv_sock.listen(1)
        SERVER_LOGGER.info(f'Запущен сервер с параметрами адресс: {args.addr}, порт: {args.port}')
    except:
        SERVER_LOGGER.error(f'Не удалось запустить сервер с параметрами адресс: {args.addr}, порт: {args.port}')
    return serv_sock


def send_and_get_msg(serv_sock):
    try:
        while True:
            client_sock, addr = serv_sock.accept()
            data = client_sock.recv(MAX_PACKAGE_LENGTH)
            request = json.loads(data.decode(ENCODING))
            SERVER_LOGGER.debug(f'Получено сообщение от клиента: {request}')
            if request.get('action') == 'presence':
                response = {
                    'response': 200,
                    'msg': f'Hi {request.get("user")["account_name"]}'
                }
            else:
                response = {
                    'response': 400,
                    'error': 'Wrong action, try again'
                }
            client_sock.send(json.dumps(response).encode(ENCODING))
            SERVER_LOGGER.debug(f'Отправлен ответ клиенту: {response}')
            client_sock.close()
            # return data
    finally:
        disconect(serv_sock)


def disconect(serv_sock):
    serv_sock.close()


if __name__ == '__main__':
    args = args_parser()
    serv_sock = server_socket(args)
    send_and_get_msg(serv_sock)
