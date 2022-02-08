import platform
import subprocess
from ipaddress import ip_address


def host_ping(host_list):
    host_up = []
    host_down = []
    result = {}
    for host in host_list:
        try:
            ip = str(ip_address(host))
        except ValueError:
            ip = str(host)
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        response = subprocess.Popen(['ping', param, '1', '-w', '1', ip], stdout=subprocess.PIPE)
        if response.wait() == 0:
            print(f'Узел {ip} - доступен')
            host_up.append(ip)
        else:
            print(f'Узел {ip} - не доступен')
            host_down.append(ip)
        result['Доступные узлы'] = host_up
        result['Не доступные узлы'] = host_down
    return result


if __name__ == '__main__':
    host_list = ['ya.ru', '8.8.8.8', 'asdas', 'blablabla.com', '10.10.10.10']
    print(host_ping(host_list))
