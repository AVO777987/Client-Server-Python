"""
4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового
представления в байтовое и выполнить обратное преобразование (используя методы encode и decode).
"""


def encode_decode_str(value_list):
    for item in value_list:
        print(f'Значение до преобразования: {item}')
        item = item.encode('utf-8')
        print(f'Значение в UTF-8: {item}')
        item = item.decode('utf-8')
        print(f'Значение после преобразования: {item}')
        print(f'---------------------------')


val_1 = 'разработка'
val_2 = 'администрирование'
val_3 = 'protocol'
val_4 = 'standard'

value_list = [val_1, val_2, val_3, val_4]
encode_decode_str(value_list)
