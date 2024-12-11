import math
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QPushButton, QSpinBox, QLabel


class CandleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.h0 = 200
        self.height = self.h0
        self.burning = False
        self.v = 1
        self.I = 1
        self.time = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_candle(painter)
        self.draw_flame(painter)

    def set_flame_intensity(self, value):
        self.I = value

    def reset_candle(self):
        self.timer.stop()
        self.time = 0
        self.height = self.h0
        self.burning = False
        self.update()

    def start_burning(self):
        self.time = 0
        self.burning = True
        self.timer.start(16)

    def set_height(self, value):
        self.height = value
        self.h0 = value
        self.update()

    def set_burning_speed(self, value):
        self.v = value / 10

    def update_animation(self):
        if self.height > 0:
            self.time += 0.05
            self.height = max(0, self.h0 - self.v * self.time)
            self.update()
        else:
            self.timer.stop()

    def draw_candle(self, painter):
        painter.setBrush(QColor(245, 195, 194))
        painter.drawRect(100, int(300 - self.height), 50, int(self.height))

    def draw_flame(self, painter):
        if self.height > 0:
            k = 10
            A = self.I * k
            m = 2
            omega = self.I * m
            y_offset = A * math.sin(omega * self.time)
            painter.setBrush(QColor(255, 200, 0))
            painter.drawEllipse(110, int(300 - self.height - 30 + y_offset), 30, 30)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Симуляция горения свечи")
        self.candle = CandleWidget()
        self.height_slider = QSlider(Qt.Orientation.Horizontal)
        self.height_slider.setRange(50, 300)
        self.height_slider.setValue(200)
        self.height_slider.valueChanged.connect(self.candle.set_height)
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(1)
        self.speed_slider.valueChanged.connect(self.candle.set_burning_speed)
        self.intensity_spinbox = QSpinBox()
        self.intensity_spinbox.setRange(1, 10)
        self.intensity_spinbox.setValue(1)
        self.intensity_spinbox.valueChanged.connect(self.candle.set_flame_intensity)
        self.start_button = QPushButton("Запустить анимацию")
        self.start_button.clicked.connect(self.candle.start_burning)
        self.reset_button = QPushButton("Остановить анимацию")
        self.reset_button.clicked.connect(self.candle.reset_candle)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Высота свечи"))
        layout.addWidget(self.height_slider)
        layout.addWidget(QLabel("Скорость горения"))
        layout.addWidget(self.speed_slider)
        layout.addWidget(QLabel("Интенсивность горения"))
        layout.addWidget(self.intensity_spinbox)
        layout.addWidget(self.start_button)
        layout.addWidget(self.reset_button)
        layout.addWidget(self.candle)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(400, 500)
    window.show()
    sys.exit(app.exec())
