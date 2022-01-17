"""
1. Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и проверить
тип и содержание соответствующих переменных. Затем с помощью онлайн-конвертера преобразовать строковые
представление в формат Unicode и также проверить тип и содержимое переменных.
"""


def print_value_and_type(value_list):
    for item in value_list:
        print(f'Значение: {item}')
        print(f'Тип: {type(item)}')
        print(f'---------------------------')


val_1 = 'разработка'
val_2 = 'сокет'
val_3 = 'декоратор'

value_list = [val_1, val_2, val_3]
print_value_and_type(value_list)

val_1_unicode = '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'
val_2_unicode = '\u0441\u043e\u043a\u0435\u0442'
val_3_unicode = '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'

value_list = [val_1_unicode, val_2_unicode, val_3_unicode]
print_value_and_type(value_list)
