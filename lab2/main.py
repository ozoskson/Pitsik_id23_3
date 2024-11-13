import math
import sys
from random import random
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QBrush, QColor
from PyQt6.QtWidgets import QApplication, QWidget

class AnimationArea(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sheep and Cabbage Simulation')  # Заголовок окна
        self.setGeometry(100, 100, 600, 600)  # Устанавливаем размеры и положение окна
        self.radius = 200  # Радиус окружности
        self.center_x = self.width() // 2  # Центр по оси X
        self.center_y = self.height() // 2  # Центр по оси Y
        self.animation_speed = 7  # Скорость анимации

        # Создаём капусту и овец
        self.cabbages = [Cabbage(self.radius, [self.center_x, self.center_y]) for _ in range(5)]
        self.sheep = [Sheep(self.radius, [self.center_x, self.center_y])]

        # Таймер для регулярного обновления сцены
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)  # Связываем таймер с методом обновления
        self.timer.start(16)  # Настраиваем таймер на 16 мс

    def update_display(self):
        """Метод для обновления отображения."""
        self.update()  # Перерисовываем виджет

    def create_cabbage(self):
        """Создание новой капусты с проверкой на перекрытие."""
        new_cabbage = Cabbage(self.radius, [self.center_x, self.center_y])

        # Генерация новых координат, если капуста пересекается с другими
        while any(self.check_overlap(new_cabbage, existing) for existing in self.cabbages):
            new_cabbage.generate_coordinates()
        return new_cabbage

    def check_overlap(self, cabbage1, cabbage2):
        """Проверяем, пересекаются ли капусты."""
        distance = math.sqrt((cabbage1.x - cabbage2.x) ** 2 + (cabbage1.y - cabbage2.y) ** 2)
        return distance < cabbage1.size + cabbage2.size  # Возвращаем True, если есть перекрытие

    def find_closest_cabbage(self):
        """Найти ближайшую капусту к овцам."""
        min_distance = float('inf')
        nearest_cabbage = None

        for cabbage in self.cabbages:
            for sheep in self.sheep:
                distance = math.sqrt((cabbage.x - sheep.x) ** 2 + (cabbage.y - sheep.y) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_cabbage = cabbage

        return nearest_cabbage  # Возвращаем ближайшую капусту

    def paintEvent(self, event):
        """Метод для рисования на экране."""
        painter = QPainter(self)

        # Рисуем розовый круг
        painter.setBrush(QBrush(QColor(255, 192, 203), Qt.BrushStyle.SolidPattern))  # Розовый цвет
        painter.drawEllipse(self.center_x - self.radius, self.center_y - self.radius, self.radius * 2, self.radius * 2)

        self.target_cabbage = self.find_closest_cabbage()  # Находим цель - ближайшую капусту
        for cabbage in self.cabbages:
            # Получаем координаты капусты
            cabbage_x = cabbage.x
            cabbage_y = cabbage.y

            # Рисуем капусту зелёного цвета
            painter.setBrush(QBrush(QColor(0, 255, 0), Qt.BrushStyle.SolidPattern))
            painter.drawEllipse(int(cabbage_x - 5), int(cabbage_y) - 5, int(cabbage.size), int(cabbage.size))

        # Получаем список расстояний между овцами и целью
        distances = self.move_sheep()

        # Копируем список овец
        sheep_copy = self.sheep[:]

        for index, sheep in enumerate(sheep_copy):
            if sheep.hungry <= 0:  # Если овца голодна
                sheep.exist = False
                self.sheep.remove(sheep)
                Sheep.TOTAL_SHEEP -= 1
                if Sheep.TOTAL_SHEEP == 0:
                    print("Все овцы погибли. Не повезло :(")
                    sys.exit(app.exec())
            else:
                sheep_x = sheep.x
                sheep_y = sheep.y

                if index < len(distances) and distances[index] < 20:  # Если овца рядом с капустой
                    sheep.hungry += sheep.eat_speed
                    self.target_cabbage.value -= sheep.eat_speed
                    if self.target_cabbage.value <= 0:  # Если капуста исчерпана
                        self.cabbages.remove(self.target_cabbage)
                        self.target_cabbage = self.create_cabbage()
                        self.cabbages.append(self.target_cabbage)
                else:
                    sheep.hungry -= 1  # Уменьшаем голод

                # Проверяем возможность воспроизводства
                if sheep.hungry > sheep.reproduction_threshold:
                    sheep.hungry -= 300  # Ограничиваем голод для воспроизводства
                    sheep.size += 10  # Увеличиваем размер овцы

                # Рисуем овцу
                painter.setBrush(QBrush(QColor(0, 0, 0), Qt.BrushStyle.SolidPattern))  # Чёрный цвет для овцы
                painter.drawEllipse(int(sheep_x - 5), int(sheep_y - 5), sheep.size, sheep.size)

    def move_sheep(self):
        """Перемещаем овец к ближайшей капусте."""
        distance_list = []
        for sheep in self.sheep:
            dx = self.target_cabbage.x - sheep.x
            dy = self.target_cabbage.y - sheep.y

            distance = math.sqrt(dx ** 2 + dy ** 2)
            distance_list.append(distance)
            if distance > self.target_cabbage.size - 2:  # Если овца далеко от капусты
                sheep.x += sheep.speed * (dx / distance)
                sheep.y += sheep.speed * (dy / distance)
        return distance_list  # Возвращаем расстояния

class Cabbage:
    def __init__(self, circle_radius, center):
        self.center = center
        self.circle_radius = circle_radius
        self.exist = False
        self.generate_coordinates()  # Генерируем координаты
        self.value = int((random() + 0.1) * 400)  # Устанавливаем значение капусты
        self.size = 2 * math.log(self.value)  # Определяем размер капусты

    def generate_coordinates(self):
        """Генерация случайных координат для капусты."""
        range_val = random() * (self.circle_radius * 0.95)
        angle = random() * 360
        self.x = self.center[0] + range_val * math.cos(math.radians(angle))
        self.y = self.center[1] + range_val * math.sin(math.radians(angle))
        self.value = int((random() + 0.1) * 400)  # Обновляем значение капусты

class Sheep:
    TOTAL_SHEEP = 0  # Общее число овец

    def __init__(self, circle_radius, center):
        Sheep.TOTAL_SHEEP += 1  # Увеличиваем общее количество овец
        self.center = center
        self.circle_radius = circle_radius
        self.speed = random()  # Устанавливаем случайную скорость
        self.hungry = (random() + 0.1) * 1000  # Устанавливаем начальное значение голода
        self.reproduction_threshold = (random() + 0.1) * 2000  # Порог для воспроизводства
        self.eat_speed = random() + 1  # Скорость поедания
        self.generate_coordinates()  # Генерация координат овцы
        print(f'Создана овца: скорость={self.speed}; голод={self.hungry}; порог воспроизводства={self.reproduction_threshold}; скорость поедания={self.eat_speed}; общее количество овец={Sheep.TOTAL_SHEEP}')
        self.size = int(self.hungry // 40)  # Устанавливаем размер овцы

    def generate_coordinates(self):
        """Генерация случайных координат для овцы."""
        range_val = random() * (self.circle_radius * 0.95)
        angle = random() * 360
        self.x = self.center[0] + range_val * math.cos(math.radians(angle))
        self.y = self.center[1] + range_val * math.sin(math.radians(angle))

if __name__ == '__main__':
    app = QApplication(sys.argv)  # Создание приложения
    window = AnimationArea()  # Создание окна анимации
    window.show()  # Отображение окна
    sys.exit(app.exec())  # Запуск главного цикла приложения