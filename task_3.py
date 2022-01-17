"""
3. Определить, какие из слов, поданных на вход программы, невозможно записать в байтовом типе. Для проверки
правильности работы кода используйте значения: «attribute», «класс», «функция», «type»
"""


def print_value(value_list):
    for item in value_list:
        try:
            print(f'Значение: {item}')
            item = eval(f"b'{item}'")
            print(f'Тип: {type(item)}')
        except SyntaxError:
            print('Не возможно перевести строку к битовому формату, так как есть не соответствие таблице ASCII')


val_1 = 'attribute'
val_2 = 'класс'
val_3 = 'функция'
val_4 = 'type'

value_list = [val_1, val_2, val_3, val_4]
print_value(value_list)
