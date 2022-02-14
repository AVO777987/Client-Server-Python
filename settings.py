import logging
# Настройки подключения
DEFAULT_SERVER_LISTEN_PORT = 7777
DEFAULT_SERVER_LISTEN_IP = '127.0.0.1'
DEFAULT_REMOTE_SERVER_PORT = 7777
DEFAULT_REMOTE_SERVER_IP = '127.0.0.1'
# Настройки взаимодействия
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'
# Настройки логирования
LOGGING_LEVEL_SERVER = logging.DEBUG
LOGGING_LEVEL_CLIENT = logging.DEBUG
LOGGING_FORMAT_SERVER = '%(asctime)s %(levelname)-8s %(filename)s %(message)s'
LOGGING_FORMAT_CLIENT = '%(asctime)s %(levelname)-8s %(filename)s %(message)s'
