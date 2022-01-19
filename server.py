import argparse
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import json


def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', help='Listen port', default=7777)
    parser.add_argument('--addr', '-a', help='Listen IP', default='')
    args = parser.parse_args()
    return args


def serv_sock(args):
    serv_sock = socket(AF_INET, SOCK_STREAM)
    serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serv_sock.bind((args.addr, int(args.port)))
    serv_sock.listen(1)
    return serv_sock


def send_and_get_msg(serv_sock):
    try:
        while True:
            client_sock, addr = serv_sock.accept()
            data = client_sock.recv(4096)
            request = json.loads(data.decode('utf-8'))
            print(f'Пришло сообщение {request}')
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
            client_sock.send(json.dumps(response).encode('utf-8'))
            client_sock.close()
    finally:
        disconect(serv_sock)


def disconect(serv_sock):
    serv_sock.close()


if __name__ == '__main__':
    args = args_parser()
    serv_sock = serv_sock(args)
    send_and_get_msg(serv_sock)
