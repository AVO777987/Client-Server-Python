"""
3. Задание на закрепление знаний по модулю yaml. Написать скрипт, автоматизирующий сохранение данных в файле
YAML-формата. Для этого:
Подготовить данные для записи в виде словаря, в котором первому ключу соответствует список, второму — целое число,
третьему — вложенный словарь, где значение каждого ключа — это целое число с юникод-символом, отсутствующим в кодировке
ASCII (например, €);
Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml. При этом обеспечить стилизацию файла
с помощью параметра default_flow_style, а также установить возможность работы с юникодом: allow_unicode = True;
Реализовать считывание данных из созданного файла и проверить, совпадают ли они с исходными.
"""

import yaml


def write_to_yaml(data):
    with open('file.yaml', 'w') as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)

    with open('file.yaml') as file:
        print(file.read())


if __name__ == "__main__":
    data = {
        'key_1': ['Samsung', 'Apple', 'Huawey', 'Nokia'],
        'key_2': 13,
        'key_3': {
            'val_1': '100$',
            'val_2': '100€',
            'val_3': '100А',
            'val_4': '100Б',
            }
        }
    write_to_yaml(data)

