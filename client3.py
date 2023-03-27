#!/usr/bin/python3

import select
import socket
import json
import time
from threading import Thread
import clock_lib

server_address = ('localhost', 50000)

hostname = "client3"

client_i = 0

SOCKET_LIST = list()
SEND_LIST = list()

input_msg_queue = list()

#request_time = 0
#response_time = 0

# Определяем переменную, в которой будет храниться структура json
apod_dict = {"type": "",
             "to": "",
             "from": "",
             "msg": ""}


def handle_readables(read_sockets):
    # Обработка появления событий на входах
    for resource in read_sockets:
        data = ""
        try:
            data_json = resource.recv(1024)

        # Если сокет был закрыт на другой стороне
        except ConnectionResetError:
            pass

        if data_json:
            # print(data_json)
            # Вывод полученных данных на консоль
            apod_dict = json.loads(data_json.decode())

            # Говорим о том, что мы будем еще и писать в данный сокет
            if apod_dict["type"] == "msg":
                print("Recieve msg from {address}: {msg}".format(
                    address=apod_dict["from"], msg=apod_dict["msg"]))
            elif apod_dict["type"] == "clk_synk":
                print("reciev time sync")
                #responce_time = time.time()
                clock_lib.clock_curant = apod_dict["msg"]
            elif apod_dict["type"] == "clk_get":
                print("get time request")
                queue_item = ("clk_time", "", hostname, time.time() + 900)
                input_msg_queue.append(queue_item)


def clear_resource(resource):
    # Метод очистки ресурсов использования сокета
    if resource in SOCKET_LIST:
        SOCKET_LIST.remove(resource)
    resource.close()


def worker():
    while 1:
        try:
            read_sockets, write_sockets, error_sockets = \
                select.select(SOCKET_LIST, [], [])
            handle_readables(read_sockets)
        except KeyboardInterrupt:
            clear_resource(s)
            print("Client stopped! Thank you for using!")
            break


def messenger():
    apod_dict = {}
    while(True):
        for item_msg in input_msg_queue:
            (msg_type, msg_to, msg_from, msg) = item_msg
            # Формируем ответ для клиента в форме json
            apod_dict["type"] = msg_type
            apod_dict["t0"] = msg_to
            apod_dict["from"] = msg_from
            apod_dict["msg"] = msg

            data_json = json.dumps(apod_dict)
            s.sendall(data_json.encode("utf-8"))

            input_msg_queue.remove(item_msg)


time.sleep(60)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(server_address)

apod_dict["type"] = "reg"
apod_dict["from"] = hostname

data_json = json.dumps(apod_dict)
s.send(data_json.encode('utf-8'))

SOCKET_LIST.append(s)

Thread(target=clock_lib.clock_face, args=("Часы3",)).start()

Thread(target=worker).start()

Thread(target=messenger).start()

while len(SOCKET_LIST) > 0:
    time.sleep(120)
