from tabulate import tabulate

from task2 import host_range_ping


def host_range_ping_tab():
    print(tabulate(host_range_ping(), headers='keys'))


if __name__ == '__main__':
    host_range_ping_tab()
