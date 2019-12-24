
"""
@author: hyt
@time：2019-03-27
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from work_box.define import *
from work_box.tools import getYaml, Device
from work_box.shell import ADB

from .issue import Issue

class PaintArea(QWidget):
    def __init__(self):
        super(PaintArea,self).__init__()

        self._w = self.size().width()
        self._h = self.size().height()
        self._width = self._w 
        self._height = self._h


        self.setPalette(QPalette(Qt.white))
        self.setAutoFillBackground(True)
        # self.setFixedSize(self._h, self._w)
        self.image_path = ""
        self.pen = QPen(QColor('red'),3)

        self.start_flag = False
        self.end_flag = False

        self.start_point = None
        self.end_point = None

    def mousePressEvent(self, e):
        x = e.x()
        y = e.y()

        x = x * self._width / self._w
        y = y * self._height / self._h

        if self.start_flag:
            self.start_point = QPoint(x, y)
            self.setCursor(Qt.ArrowCursor)
            self.update()
            self.start_flag = False

        elif self.end_flag:
            self.end_point = QPoint(x, y)
            self.setCursor(Qt.ArrowCursor)
            self.update()
            self.end_flag = False
    
    def getPoint(self):
        sx = self.start_point.x() / self._width
        sy = self.start_point.y() / self._height

        ex = self.end_point.x() / self._width
        ey = self.end_point.y() / self._height

        return (sx, sy, ex, ey)

    def start(self):
        self.start_flag = True
        self.end_flag = False
        self.setCursor(Qt.CrossCursor)
    
    def end(self):
        self.start_flag = False
        self.end_flag = True
        self.setCursor(Qt.CrossCursor)

    def setImage(self, file_name):
        self.image_path = file_name
        self.update()

    def paintEvent(self, QPaintEvent):
        p = QPainter(self)
        self._w , self._h = self.size().width(), self.size().height()

        if os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            self._width = pixmap.width()
            self._height = pixmap.height()

            if pixmap.width() > pixmap.height():
                pixmap = pixmap.scaled(self._w, self._h, aspectRatioMode=Qt.KeepAspectRatio)
                self.resize(pixmap.width(), pixmap.height())
            else:
                pixmap = pixmap.scaled(self._h, self._w,aspectRatioMode=Qt.KeepAspectRatio)
                self.resize(pixmap.width(), pixmap.height())
            p.drawPixmap(0, 0, pixmap)

        if self.start_point:
            p.setPen(QPen(QColor('red'),2))
            x = self.start_point.x() * self._w / self._width
            y = self.start_point.y() * self._h / self._height
            p.drawEllipse(x-5, y-5, 10,10)

        if self.end_point:
            p.setPen(QPen(QColor('blue'),2))
            x_ = self.end_point.x() * self._w / self._width
            y_ = self.end_point.y() * self._h / self._height
            p.drawEllipse(x_-5, y_-5, 10,10)

        if self.start_point and self.end_point:
            p.setPen(QPen(QColor('black'),3))
            # p.drawLine(self.start_point, self.end_point)
            p.drawLine(x, y , x_, y_)

class SwipPaintDialog(QFrame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.issue = Issue.get_init()
        self.shotcut_button = QPushButton("截图")
        self.start_button = QPushButton("起点")
        self.end_button = QPushButton("终端")
        self.get_button = QPushButton("提取")
        self.area = PaintArea()

        self.setLayouts()
        self.setStyle()
        self.config()

    def config(self):
        self.shotcut_button.clicked.connect(self.screenshot)
        self.start_button.clicked.connect(self.start)
        self.end_button.clicked.connect(self.end)
        self.get_button.clicked.connect(self.accept)

        self.issue.reg(Issue.CHANEG_TIER, self.show_item) 

    def setStyle(self):
        self.shotcut_button.setFixedSize(150,30)
        self.start_button.setFixedSize(150,30)
        self.end_button.setFixedSize(150,30)
        self.get_button.setFixedSize(150,30)

    def setLayouts(self):
        layout = QHBoxLayout()
        layout.addWidget(self.area)    

        item_layout = QVBoxLayout()
        item_layout.addWidget(self.shotcut_button)
        item_layout.addWidget(self.start_button)
        item_layout.addWidget(self.end_button)
        item_layout.addWidget(self.get_button)
        item_layout.addStretch(1)

        layout.addLayout(item_layout)
        self.setLayout(layout)

    def accept(self):
        if self.area.start_point and self.area.end_point:
            point = self.area.getPoint()
            self.issue.send(Issue.SEND_SWIP_POINT, point)

    def start(self):
        self.area.start()

    def end(self):
        self.area.end()

    def screenshot(self):
        self.issue.send(Issue.SCREENSHOT)

    def show_item(self, dump, png_path):
        self.area.setImage(png_path)
