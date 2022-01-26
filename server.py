import argparse
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import json
import logging

from utils import get_msg, send_msg
from settings import DEFAULT_SERVER_LISTEN_IP, DEFAULT_SERVER_LISTEN_PORT, ENCODING, MAX_PACKAGE_LENGTH
from log_decorator import log
import logs.config_server_log

SERVER_LOGGER = logging.getLogger('server')


@log
def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', help='Listen port', default=DEFAULT_SERVER_LISTEN_PORT)
    parser.add_argument('--addr', '-a', help='Listen IP', default=DEFAULT_SERVER_LISTEN_IP)
    args = parser.parse_args()
    return args


@log
def server_socket(args):
    server_sock = socket(AF_INET, SOCK_STREAM)
    server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    try:
        server_sock.bind((args.addr, int(args.port)))
        server_sock.listen(1)
        SERVER_LOGGER.info(f'Запущен сервер с параметрами адресс: {args.addr}, порт: {args.port}')
    except:
        SERVER_LOGGER.error(f'Не удалось запустить сервер с параметрами адресс: {args.addr}, порт: {args.port}')
    return server_sock


@log
def create_response(request):
    if request.get('action') == 'presence':
        response = json.dumps(
            {
                'response': 200,
                'msg': f'Hi {request.get("user")}'
            }
        )
    else:
        response = json.dumps(
            {
                'response': 400,
                'error': 'Wrong action, try again'
            }
        )
    return response

@log
def disconect(serv_sock):
    serv_sock.close()


def main():
    server_sock = server_socket(args_parser())
    try:
        while True:
            client_sock, addr = server_sock.accept()
            request = get_msg(client_sock)
            SERVER_LOGGER.debug(f'Получено сообщение от клиента: {request}')
            response = create_response(request)
            send_msg(response, client_sock)
            SERVER_LOGGER.debug(f'Отправлен ответ клиенту: {response}')
            client_sock.close()
    finally:
        disconect(server_sock)


if __name__ == '__main__':
    main()
