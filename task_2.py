"""
2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с информацией о заказах. Написать
скрипт, автоматизирующий его заполнение данными. Для этого:
Создать функцию write_order_to_json(), в которую передается 5 параметров — товар (item), количество (quantity),
цена (price), покупатель (buyer), дата (date). В это словаре параметров обязательно должны присутствовать
юникод-символы, отсутствующие в кодировке ASCII.
Функция должна предусматривать запись данных в виде словаря в файл orders.json. При записи данных указать величину
отступа в 4 пробельных символа;
Необходимо также установить возможность отображения символов юникода: ensure_ascii=False;
Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра.
"""
import json


def write_order_to_json(item, quantity, price, buyer, date):
    with open('orders.json') as file:
        dict_to_json = json.load(file)
        dict_to_json['orders'].append({
            'item': item,
            'quantity': quantity,
            'price': price,
            'buyer': buyer,
            'date': date,
        })
        print(dict_to_json)
    with open('orders.json', 'w') as file:
        json.dump(dict_to_json, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    write_order_to_json('Samsung', 10, 30000, 'Иванов Иван', '01.01.2022')
    write_order_to_json('Apple', 12, 70000, 'Петров Петр', '02.01.2022')
    write_order_to_json('Huawey', 23, 13400, 'Андреев Андрей', '03.01.2022')
    write_order_to_json('Nokia', 24, 12500, 'Васильев Василий', '04.01.2022')

