import math
import sys
from random import random

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QBrush, QColor, QMouseEvent
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QSlider, QLabel, QHBoxLayout
from PyQt6.QtWidgets import QDialog, QFormLayout, QSpinBox


# Анимация поедания

class CircleAnimation(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Garden')
        self.setGeometry(25, 25, 900, 600)
        self.is_paused = False
        self.y_center = self.height() // 2
        self.x_center = (self.width() - 300) // 2
        self.speed = 2  # скорость анимации
        self.range = 200  # радиус окружности

        self.herds = [Herd(20, [self.x_center, self.y_center])]
        self.cabbages = [Cabbage(self.range, [self.x_center, self.y_center]) for _ in range(5)]

        # Таймер для обновления игры
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(16)
        self.init_user_interface()

    def update_position(self):
        if not self.is_paused:
            # Если игра не на паузе, то обновляем
            self.update()

    def init_user_interface(self):
        main_layout = QHBoxLayout(self)

        # Основная область визуализации
        self.canvas = QWidget(self)
        self.canvas.setMinimumSize(600, 600)
        main_layout.addWidget(self.canvas)

        # Панель управления
        control_panel = QVBoxLayout()

        # Добавление слайдеров
        self.speed_slider = self.add_slider("Скорость стада", 1, 10, 5, control_panel)
        self.endurance_slider = self.add_slider("Выносливость", 100, 1000, 500, control_panel)
        self.eat_speed_slider = self.add_slider("Скорость поедания", 1, 5, 2, control_panel)
        self.reproduction_slider = self.add_slider("Репродуктивность", 100, 2000, 1000, control_panel)

        add_sheep_btn = QPushButton("Добавить стадо", self)
        add_sheep_btn.clicked.connect(self.add_herd)
        control_panel.addWidget(add_sheep_btn)

        main_layout.addLayout(control_panel)
        self.setLayout(main_layout)

    def is_overlay(self, cabbage1, cabbage2):
        # Проверка на пересечение с учетом радиусов капуст
        distance = math.sqrt((cabbage1.y - cabbage2.y) ** 2 + (cabbage1.x - cabbage2.x) ** 2)
        return distance < cabbage2.size + cabbage1.size

    def add_slider(self, label_text, min_val, max_val, default_val, layout):
        label = QLabel(label_text, self)
        slider = QSlider(Qt.Orientation.Horizontal, self)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setTickInterval((max_val - min_val) // 5)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        layout.addWidget(label)
        layout.addWidget(slider)
        return slider

    def add_new_cabbage(self):
        # Создаем новую капусту
        new_cabbage = Cabbage(self.range, [self.x_center, self.y_center])

        # Пока новая капуста пересекается с существующими, генерируем новые координаты
        while any(self.is_overlay(new_cabbage, existing) for existing in self.cabbages):
            new_cabbage.create_coordinates()

        return new_cabbage

    def add_herd(self):  # Добавление овцы
        # Создаём овцу
        new_sheep = Herd(20, [self.x_center, self.y_center])
        # Настраиваем параметры овцы по данным со слайдеров
        new_sheep.eat_speed = self.eat_speed_slider.value()
        new_sheep.speed = self.speed_slider.value()
        new_sheep.breeding = self.reproduction_slider.value()
        new_sheep.hungry = self.endurance_slider.value()
        # Добавляем новое стадо в общую массу
        self.herds.append(new_sheep)

    def select_purpose_cabbage(self):
        # Функция поиска ближайшей капусты, которая станет целью стад
        nearest_cabbage = None
        min_distance = float('inf')
        # Поиск перебором "Всех со всеми"
        for cabbage in self.cabbages:
            for sheep in self.herds:
                distance = math.sqrt((cabbage.y - sheep.y) ** 2 + (cabbage.x - sheep.x) ** 2)
                if distance < min_distance:
                    nearest_cabbage = cabbage
                    min_distance = distance
        return nearest_cabbage  # Выбор минимального

    def sheep_edit_inteface(self, sheep):
        # Создаём окно изменения овцы
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование овцы")
        layout = QFormLayout(dialog)

        # Параметр скорости овцы
        eat_speed_spin = QSpinBox(dialog)
        eat_speed_spin.setValue(int(sheep.eat_speed * 33))
        layout.addRow("Скорость поедания", eat_speed_spin)

        # Параметр скорости стада
        speed_spin = QSpinBox(dialog)
        speed_spin.setValue(int(sheep.speed * 100))
        layout.addRow("Скорость", speed_spin)

        # Параметр репродуктивности
        reproduction_spin = QSpinBox(dialog)
        reproduction_spin.setValue(int(sheep.breeding / 24))
        layout.addRow("Плодовитость", reproduction_spin)

        # Параметр голода
        hungry_spin = QSpinBox(dialog)
        hungry_spin.setValue(int(sheep.hungry / 12))
        layout.addRow("Голод", hungry_spin)

        # Кнопка применить вызывает функцию
        ok_button = QPushButton("Применить", dialog)
        ok_button.clicked.connect(
            lambda: self.update_herds_settings(dialog, sheep, speed_spin, eat_speed_spin, hungry_spin,
                                               reproduction_spin))
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        dialog.exec()

    def herds_moving(self):
        # Считаем новые координаты для овец
        distance_list = []
        for sheep in self.herds:
            # Расстояние между овцой и целевой капустой
            dy = self.purpose_cabbage.y - sheep.y
            dx = self.purpose_cabbage.x - sheep.x
            distance = math.sqrt(dy ** 2 + dx ** 2)
            if distance > self.purpose_cabbage.size - 2:
                # Если капуста всё ещё далеко, то считаем новые координаты
                sheep.y += sheep.speed * (dy / distance)
                sheep.x += sheep.speed * (dx / distance)
            # Добавляем это расстояние в список на ответ
            distance_list.append(distance)
        return distance_list

    def update_herds_settings(self, dialog, sheep, speed_spin, eat_speed_spin, hungry_spin, reproduction_spin):
        # Применяем новые параметры с переводом из 100 бальной системы
        sheep.hungry = hungry_spin.value() * 15
        sheep.size = int(hungry_spin.value() * 12 / 40)
        sheep.speed = speed_spin.value() / 100
        sheep.breeding = reproduction_spin.value() * 24
        sheep.eat_speed = eat_speed_spin.value() / 33
        dialog.accept()

    def paintEvent(self, event, **kwargs):
        # Функция отрисовки
        painter = QPainter(self)
        self.purpose_cabbage = self.select_purpose_cabbage()

        # Окружность
        painter.setBrush(QBrush(QColor(173,255,47), Qt.BrushStyle.SolidPattern))
        painter.drawEllipse(self.x_center - self.range, self.y_center - self.range, self.range * 2, self.range * 2)
        for cabbage in self.cabbages:
            # Задаём координаты капусты
            cabbage_y = cabbage.y
            cabbage_x = cabbage.x
            # Капуста
            painter.setBrush(QBrush(QColor(0, 128, 0), Qt.BrushStyle.SolidPattern))
            painter.drawEllipse(int(cabbage_x - 5), int(cabbage_y) - 5, int(cabbage.size), int(cabbage.size))

        # Вычисляем расстояния
        distances = self.herds_moving()

        # Создаем копию списка овец, чтобы избежать ошибок индексации
        herds_copy = self.herds[:]

        # Проходим по каждой овце и высчитываем для них параметры
        for id, sheep in enumerate(herds_copy):
            if sheep.hungry <= 0:  # Если голод кончился, то стадо умирает
                Herd.SHEEP_COUNT -= 1  # Меняем общее количество стад
                self.herds.remove(sheep)
                if Herd.SHEEP_COUNT == 0:  # Если стад больше нет, то игра об этом уведомит (или закончит симмуляцию)
                    print("Кажется, все стада вымерли :(")
                    # sys.exit(app.exec())
                sheep.exist = False

            else:
                # Если голод не кончился, то обновляем координаты стада
                sheep_y = sheep.y
                sheep_x = sheep.x

                if sheep.hungry > sheep.breeding:
                    # Если голод достиг значения размножения:
                    sheep.hungry -= 300  # Уменьшаем голод овцы (чтобы не происходило множественного размножения)
                    if sheep.size < 40:  # Если размер стада достаточный, то создаём новое стадо
                        sheep.size += 10
                    else:  # Иначе увеличиваем размер стада
                        self.herds.append(Herd(20, [sheep_x, sheep_y]))

                if id < len(distances) and distances[id] < 20:  # Если стадо близко к капусте:
                    # Добавляем голод стадам и уменьшаем остаток у капусты
                    self.purpose_cabbage.value -= sheep.eat_speed
                    sheep.hungry += sheep.eat_speed
                    if self.purpose_cabbage.value <= 0:  # Удаляем капусту, если она кончилась
                        self.cabbages.remove(self.purpose_cabbage)
                        self.purpose_cabbage = self.add_new_cabbage()
                        self.cabbages.append(self.purpose_cabbage)
                    # Анимация поедания капусты стадом (рисуем полукруги)
                    painter.setBrush(QBrush(QColor(255, 255, 255), Qt.BrushStyle.SolidPattern))
                    painter.drawPie(int(sheep_x - sheep.size / 2), int(sheep_y - sheep.size / 2),
                                    sheep.size, sheep.size, 0, 180 * 16)
                else:
                    sheep.hungry -= 1  # Уменьшаем голод овцы, если она не ест
                    # Обычное отображение овцы
                    painter.setBrush(QBrush(QColor(255, 255, 255), Qt.BrushStyle.SolidPattern))
                    painter.drawEllipse(int(sheep_x - 5), int(sheep_y - 5), sheep.size, sheep.size)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_P:  # Пауза на кнопку P
            if self.is_paused:
                self.is_paused = False
            else:
                self.is_paused = True

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # Если нажимаем ЛКМ, то собираем координаты нажатия
            x = event.position().x()
            y = event.position().y()
            for sheep in self.herds:  # Смотрим, на какую овцу нажали
                distance = math.sqrt((sheep.y - y) ** 2 + (sheep.x - x) ** 2)
                if distance <= sheep.size:
                    # Проверяем координаты клика и овцы
                    self.sheep_edit_inteface(sheep)
                    return
            # Если клик был не по овце, то добавляем капусту
            self.cabbages.append(Cabbage(self.range, [x, y], generate_coords=False))
            self.update()


class Herd:
    # Класс стада
    SHEEP_COUNT = 0  # Количество оставшихся стад

    def __init__(self, circle_radius, center):
        self.center = center
        self.breeding = (random() + 0.1) * 2000  # Нужно еды для увеличения стада
        self.eat_speed = random() + 1  # Скорость поедания капусты
        self.hungry = (random() + 0.1) * 1000  # Параметр голода стада
        self.size = int(self.hungry // 40)  # Задаём размер, исходя из голода
        self.speed = random()  # Скорость стада
        self.circle_radius = circle_radius
        self.create_coordinates()  # Генерируем координаты стада
        Herd.SHEEP_COUNT += 1  # Создаём новое стадо

    def create_coordinates(self):
        angle = random() * 360
        range = random() * (self.circle_radius * 0.95)
        self.y = self.center[1] + range * math.sin(math.radians(angle))
        self.x = self.center[0] + range * math.cos(math.radians(angle))


class Cabbage:
    # Класс капусты
    def __init__(self, circle_radius, center, generate_coords=True):
        self.center = center
        self.exist = False
        self.circle_radius = circle_radius
        self.value = int((random() + 0.1) * 400)
        if not generate_coords:  # Если есть чётки координаты, то задаём их
            self.y = center[1]
            self.x = center[0]
        else:  # Генерируем координаты, если необходимо
            self.create_coordinates()
        self.size = 2 * math.log(self.value)

    def create_coordinates(self):
        range = random() * (self.circle_radius * 0.95)
        angle = random() * 360
        self.value = int((random() + 0.1) * 400)
        self.y = self.center[1] + range * math.sin(math.radians(angle))
        self.x = self.center[0] + range * math.cos(math.radians(angle))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CircleAnimation()
    window.show()
    sys.exit(app.exec())
