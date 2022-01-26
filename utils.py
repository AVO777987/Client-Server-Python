import json
import logging

from settings import ENCODING, MAX_PACKAGE_LENGTH
from log_decorator import log

CLIENT_LOGGER = logging.getLogger('client')


@log
def send_msg(msg, client_sock):
    try:
        client_sock.send(msg.encode(ENCODING))
        CLIENT_LOGGER.debug(f'Отправлено сообщение!!! {msg}')
    except AttributeError:
        CLIENT_LOGGER.error(f'Попытка отправить не JSON')
    except:
        CLIENT_LOGGER.error(f'Не удалось отправить сообщение на сервер!')


@log
def get_msg(client_sock):
    try:
        encoded_response = client_sock.recv(MAX_PACKAGE_LENGTH)
        decode_response = encoded_response.decode(ENCODING)
        data = json.loads(decode_response)
        CLIENT_LOGGER.debug(f'Получено сообщение с сервера: {data}')
    except OSError:
        CLIENT_LOGGER.error('Запрос на отправку или получение данных  (when sending on a datagram '
                            'socket using a sendto call) no address was supplied')
    return data
