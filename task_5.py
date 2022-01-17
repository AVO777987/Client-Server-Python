"""
5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из
байтового в строковый (предварительно определив кодировку выводимых сообщений).
"""
import subprocess
from sys import platform
import chardet

if platform == 'win32':
    code = '-n'
else:
    code = '-c'


def ping_url(url):
    args = ["ping", code, '6', url]
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in process.stdout:
        encoding = chardet.detect(line)
        print(line.decode(encoding['encoding']))


ping_url('yandex.ru')
ping_url('youtube.com')
