"""
6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет»,
«декоратор». Проверить кодировку созданного файла (исходить из того, что вам априори неизвестна кодировка этого файла!).
 Затем открыть этот файл и вывести его содержимое на печать. ВАЖНО: файл должен быть открыт без ошибок вне зависимости
 от того, в какой кодировке он был создан!
"""

import chardet


with open('test_file.txt', 'w') as file:
    line_str = ['сетевое программирование', 'сокет', 'декоратор']
    for line in line_str:
        file.write(f'{line}\n')

with open('test_file.txt', 'rb') as file:
    encoding = chardet.detect(file.read())


with open('test_file.txt', 'r', encoding=encoding['encoding']) as file:
    print(file.read())

