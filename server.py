import select
import socket
import queue
import json
from threading import Thread
import time
import clock_lib

SERVER_ADDRESS = ('localhost', 50000)

# Говорит о том, сколько дескрипторов может быть одновременно открыты
MAX_CONNECTIONS = 10

# Откуда и куда записывать информацию
INPUTS = list()
OUTPUTS = list()

input_conn_queue = list()
input_msg_queue = list()

sync_started = False


def create_server_socket():

    # Создаем сокет, который работает без блокирования основного потока
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Биндим сервер на нужный адрес и порт
    server.bind(SERVER_ADDRESS)

    # Установка максимального количества подключений
    server.listen(MAX_CONNECTIONS)

    return server


def handle_readables(readables, server):
    """Обработка появления событий на входах"""
    global sync_started

    for resource in readables:

        # Если событие исходит от серверного сокета, то мы получаем новое подключение
        if resource is server:
            connection, client_address = resource.accept()
            connection.setblocking(0)
            INPUTS.append(connection)
            print("new connection from {address}".format(
                address=client_address))

        # Если событие исходит не от серверного сокета, но сработало прерывание на выполнение входного буфера
        else:
            data_json = ""
            try:
                data_json = resource.recv(1024)

            # Если сокет был закрыт на другой стороне
            except ConnectionResetError:
                pass
            if data_json:
                # print(data_json)
                # Вывод полученных данных на консоль
                apod_dict = json.loads(data_json.decode())

            # Говорим о том, что мы будем еще и писать а данный сокет
                if apod_dict["type"] == "reg":
                    queue_item = (apod_dict["from"], resource, [0])
                    input_conn_queue.append(queue_item)
                    if not sync_started:
                        sync_started = True
                        print("Send time request to host")
                        start_sync()
                elif apod_dict["type"] == "msg":
                    queue_item = (
                        "msg", apod_dict["to"], apod_dict["from"], apod_dict["msg"])
                    input_msg_queue.append(queue_item)
                elif apod_dict["type"] == "clk_time":
                    print("Recieve time from host")
                    for item in input_conn_queue:
                        if item[0] == apod_dict["from"]:
                            item[2][0] = apod_dict["msg"]
                    check_sync()
        # Если данных нет, но событие сработало, то ОС нам отправляет флаг о полном прочтении ресурса и его закрыли
            else:
                clear_resource(resource)


def clear_resource(resource):
    """Метод очистки ресурсов использования сокета"""
    if resource in OUTPUTS:
        OUTPUTS.remove(resource)
    if resource in INPUTS:
        INPUTS.remove(resource)
    resource.close()

    print('closing connection' + str(resource))


def listener():
    print("server is running, please, press ctrl+c to stop")
    try:
        while INPUTS:
            readables, writables, exceptional = select.select(INPUTS, [], [])
            handle_readables(readables, server_socket)
    except KeyboardInterrupt:
        clear_resource(server_socket)
        print("Server stopped! Thank you for using!")


def woker():
    apod_dict = {}
    while(True):
        for item_msg in input_msg_queue:
            (msg_type, msg_to, msg_from, msg) = item_msg
            for item in input_conn_queue:
                # print(item[0])
                if item[0] == msg_to:
                    # Формируем ответ для клиента в формате json
                    apod_dict["type"] = msg_type
                    apod_dict["to"] = msg_to
                    apod_dict["from"] = msg_from
                    apod_dict["msg"] = msg

                    data_json = json.dumps(apod_dict)
                    item[1].sendall(data_json.encode('utf-8'))

            input_msg_queue.remove(item_msg)


def start_sync():
    global sync_started

    sync_started = True

    for item in input_conn_queue:
        queue_item = ("clk_get", item[0], "", "")
        item[2][0] = 10
        input_msg_queue.append(queue_item)


def check_sync():
    global sync_started

    if sync_started:
        print("Calc time")
        flag_sync = 0
        for item in input_conn_queue:
            if item[2][0] == 10:
                flag_sync = 1
                break
        if not flag_sync:
            print("Calc time 1")
            time_sync = 0
            for item in input_conn_queue:
                time_sync = time_sync + item[2][0]
            time_sync = time_sync + time.time()
            time_sync = time_sync / (len(input_conn_queue) + 1)
            clock_lib.clock_curant = time_sync
            for item in input_conn_queue:
                queue_item = ("clk_synk", item[0], "", time_sync)
                item[2][0] = 0
                input_msg_queue.append(queue_item)
            sync_started = False

# Создаем серверный сокет без блокирования основного потока в ожидании подключения


server_socket = create_server_socket()
INPUTS.append(server_socket)

Thread(target=clock_lib.clock_face, args=("Сервер", )).start()
clock_lib.clock_curant = time.time()

Thread(target=listener).start()

Thread(target=woker).start()

while 1:
    time.sleep(120)
