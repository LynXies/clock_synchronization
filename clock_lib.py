#!/usr/bin/python3

import math
import time
from tkinter import *

clock_curant = 0


def clock_face(title):
    root = Tk()
    root.title(title)
    # Инициализация холста 300х300
    canvas = Canvas(root, width=300, height=300)
    # Размещаем холст в нашем окне
    canvas.pack()
    # Циферблат  просто круг
    canvas.create_oval(10, 10, 290, 290, fill="lightblue")

    # Счетчик цикла
    i = 0
    # Цикл вывода секундных рисочек
    while i < 60:
        i = i + 1
        canvas.create_line(150 + 110 * math.cos(-i * 6 * math.pi/180 + math.pi/2),
                           150 - 110 *
                           math.sin(-6 * i * math.pi/180 + math.pi/2),
                           150 + 90 *
                           math.cos(-6 * i * math.pi/180 + math.pi/2),
                           150 - 90 *
                           math.sin(-6 * i * math.pi/180 + math.pi/2),
                           width=2)
        # Когда i кратно 5 выводим более жирную рисочку для обозначения часов
        if i % 5 == 0:
            canvas.create_line(150 + 110 * math.cos(-i * 6 * math.pi/180 + math.pi/2),
                               150 - 110 *
                               math.sin(-6 * i * math.pi/180 + math.pi/2),
                               150 + 90 *
                               math.cos(-6 * i * math.pi/180 + math.pi/2),
                               150 - 90 *
                               math.sin(-6 * i * math.pi/180 + math.pi/2),
                               width=4)
            continue

    i = 0
    # Цикл вывода цифр часов
    while i < 12:
        i += 1
        canvas.create_text(150 + 125 * math.cos(-i * 30 * math.pi/180 + math.pi/2),
                           150 - 125 *
                           math.sin(-30 * i * math.pi/180 + math.pi/2),
                           text=i, font=('Arial', 16))

    # Основной бесконечный цикл
    while 1:
        global clock_curant
        # Получаем текущее время в виде
        time_now = time.localtime(clock_curant)

        # Получаем секунды из переменной time_now
        time_sec = int(time.strftime("%S", time_now))
        # Получаем часы из переменной time_now
        time_hour = int(time.strftime("%I", time_now))
        # Получаем минуты из переменной time_now
        time_min = int(time.strftime("%M", time_now))
        # Угол отклонения секундной стрелки за 1 секунду
        sec_angle = 6 * time_sec
        # Угол отклонения минутной стрелки за 1 секунду
        min_angle = 6 * (time_min + (1/60) * time_sec)
        # Угол отклонения часовой стрелки за 1 секунду
        hour_angle = 30 * (time_hour + (1/60) * time_min)

        # Рисуем минутную стрелку
        line_min = canvas.create_line(150,
                                      150,
                                      150 - 110 *
                                      math.cos(min_angle * math.pi /
                                               180 + math.pi/2),
                                      150 - 110 *
                                      math.sin(min_angle * math.pi /
                                               180 + math.pi/2),
                                      width=3, fill='darkblue')
        # Рисуем часовую стрелку
        line_hour = canvas.create_line(150,
                                       150,
                                       150 - 90 *
                                       math.cos(hour_angle * math.pi /
                                                180 + math.pi/2),
                                       150 - 90 *
                                       math.sin(hour_angle * math.pi /
                                                180 + math.pi/2),
                                       width=5, fill='darkblue')
        # Рисуем секундную стрелку
        line_sec = canvas.create_line(150,
                                      150,
                                      150 - 110 *
                                      math.cos(sec_angle * math.pi /
                                               180 + math.pi/2),
                                      150 - 110 *
                                      math.sin(sec_angle * math.pi /
                                               180 + math.pi/2),
                                      width=2, fill='red')

        # Обновляем экран/холст
        root.update()
        # Удаляем секундную стрелку
        canvas.delete(line_sec)
        # Удаляем минутную стрелку
        canvas.delete(line_min)
        # Удаляем часовую стрелку
        canvas.delete(line_hour)

        time.sleep(1)
        clock_curant = clock_curant + 1

    # Создаем постоянный цикл
    root.mainloop
