from task1 import host_ping
from ipaddress import ip_address


def host_range_ping():
    while True:
        try:
            ip_network = ip_address(input('Введите начальный ip адресс '))
        except ValueError:
            print('Вы ввели некоректный адресс, введите коректный еще раз')
        try:
            ip_range = int(input('Введите сколько ip вы хотите проверить'))
        except ValueError:
            print('Вы ввели некоректное число, введите коректное еще раз')
        last_oct = int(str(ip_network).split('.')[3])
        if (last_oct + ip_range) > 255:
            print('Слишком большое кол-во ip адресов, не должно быть больше 255')
        else:
            host_list = []
            for i in range(ip_range):
                host_list.append(ip_network + i)
            return host_ping(host_list)


if __name__ == '__main__':
    host_range_ping()
