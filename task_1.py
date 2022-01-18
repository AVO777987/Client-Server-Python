"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных из файлов
info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого:
Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание данных.
В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров «Изготовитель
системы», «Название ОС», «Код продукта», «Тип системы». Значения каждого параметра поместить в соответствующий список.
Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list, os_type_list. В этой же
функции создать главный список для хранения данных отчета — например, main_data — и поместить в него названия
столбцов отчета в виде списка: «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения для
этих столбцов также оформить в виде списка и поместить в файл main_data (также для каждого файла);
Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение данных
через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;
Проверить работу программы через вызов функции write_to_csv().
"""
import csv
import chardet
import re


def write_to_csv(file):
    main_data = get_data(['info_1.txt', 'info_2.txt', 'info_3.txt'])
    with open(file, 'w') as file:
        fn_writer = csv.writer(file)
        for row in main_data:
            fn_writer.writerow(row)


def get_data(files):
    main_data = [['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']]
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    for file_name in files:
        with open(file_name, 'rb') as file:
            encoding = chardet.detect(file.read())
        with open(file_name, 'r', encoding=encoding['encoding']) as file:
            text = file.readlines()
            for item in text:
                vendor_os = re.match(r'Изготовитель ОС:.*', item)
                name_os = re.match(r'Название ОС:.*', item)
                key_os = re.match(r'Код продукта:.*', item)
                type_os = re.match(r'Тип системы:.*', item)
                if vendor_os:
                    os_prod_list.append(vendor_os.group(0).split(':')[1].strip())
                if name_os:
                    os_name_list.append(name_os.group(0).split(':')[1].strip())
                if key_os:
                    os_code_list.append(key_os.group(0).split(':')[1].strip())
                if type_os:
                    os_type_list.append(type_os.group(0).split(':')[1].strip())
    for i in range(len(files)):
        iter_list = []
        iter_list.append(os_prod_list[i])
        iter_list.append(os_name_list[i])
        iter_list.append(os_code_list[i])
        iter_list.append(os_type_list[i])
        main_data.append(iter_list)
    return main_data


if __name__ == "__main__":
    write_to_csv('new_file.csv')


