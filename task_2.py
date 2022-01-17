"""
2. Каждое из слов «class», «function», «method» записать в байтовом типе. Сделать это необходимо в автоматическом,
а не ручном режиме с помощью добавления литеры b к текстовому значению,
(т.е. ни в коем случае не используя методы encode и decode)
и определить тип, содержимое и длину соответствующих переменных.
"""


def print_value_type_and_len(value_list):
    for item in value_list:
        item = eval(f"b'{item}'")
        print(f'Значение: {item}')
        print(f'Тип: {type(item)}')
        print(f'Длинна: {len(item)}')
        print(f'---------------------------')


val_1 = 'class'
val_2 = 'function'
val_3 = 'method'

value_list = [val_1, val_2, val_3]
print_value_type_and_len(value_list)

