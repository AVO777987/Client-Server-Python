"""
1. Реализовать простое клиент-серверное взаимодействие по протоколу JIM (JSON instant messaging):клиент отправляет
запрос серверу; сервер отвечает соответствующим кодом результата. Клиент и сервер должны быть реализованы в виде
отдельных скриптов, содержащих соответствующие функции. Функции клиента: сформировать presence-сообщение; отправить
сообщение серверу; получить ответ сервера; разобрать сообщение сервера; параметры командной строки скрипта
client.py <addr> [<port>]: addr — ip-адрес сервера; port — tcp-порт на сервере, по умолчанию 7777.
Функции сервера: принимает сообщение клиента; формирует ответ клиенту; отправляет ответ клиенту; имеет параметры
командной строки: -p <port> — TCP-порт для работы (по умолчанию использует 7777); -a <addr> — IP-адрес для
прослушивания (по умолчанию слушает все доступные адреса).
"""

from socket import socket, AF_INET, SOCK_STREAM
import json
from datetime import datetime
import argparse


def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', help='Server port', default=7777)
    parser.add_argument('--addr', '-a', help='Server IP', default='127.0.0.1')
    args = parser.parse_args()
    return args


def connect(args):
    client_sock = socket(AF_INET, SOCK_STREAM)
    client_sock.connect((args.addr, args.port))
    return client_sock


def send_msg(msg, client_sock):
    client_sock.send(msg.encode('utf-8'))


def get_msg(client_sock):
    data = json.loads(client_sock.recv(4096).decode('utf-8'))
    if data.get('response') == 200:
        print(
            f'Response Message: {data.get("response"), data.get("msg")}'
        )
    else:
        print(
            f'Error: {data.get("error")}'
        )


def disconnect(client_sock):
    client_sock.close()


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
    args = args_parser()
    client_sock = connect(args)
    send_msg(msg_presence, client_sock)
    get_msg(client_sock)
    disconnect(client_sock)


