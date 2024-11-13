from tkinter import *
import math
# Создаем главное окно приложения
root = Tk()
# Создаем холст для рисования
canvas = Canvas(root, width=600, height=600)
canvas.pack()  # Размещаем холст в окне
# Рисуем круг на холсте
canvas.create_oval(100, 100, 500, 500)# Создаем розовую точку в центре круга
point = canvas.create_oval(295, 295, 305, 305, fill="pink")

# Функция для изменения направления движения точки
def change():
    # Используем глобальную переменную direction
    global direction
    # Меняем направление на противоположное
    direction = -direction
# Создаем кнопку "Изменить направление"
b = Button(text='Изменить направление', width=15, height=15)
# Назначаем функцию change как команду для кнопки
b.config(command=change)
# Размещаем кнопку в окне
b.pack()
# Функция для перемещения точки
def move_point():
    # Используем глобальные переменные angle, direction и speed
    global angle, direction, speed
    # Вычисляем координаты x и y для точки на круге
    x =  int(300 + 200 * math.cos(math.radians(angle)))
    y = int(300 - 200 * math.sin(math.radians(angle)))
    # Перемещаем точку на холсте
    canvas.coords(point, x+7, y+7, x-7, y-7)
    # Увеличиваем угол на значение direction (1 или -1)
    angle += direction
    # Если угол стал меньше -360, сбрасываем его в 0
    if angle <= -360:
        angle = 0
    # Запускаем функцию move_point снова через заданное время
    root.after(speed, move_point)
# Начальное направление движения
direction = 1
# Начальный угол
angle = 0
# Получаем скорость движения от пользователя
speed = int(input('Выберете скорость, чем меньше-тем быстрее >0 '))
# Запускаем функцию move_point для начала движения
move_point()
# Запускаем главный цикл Tkinter
root.mainloop()

