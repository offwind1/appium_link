
"""
@author: hyt
@time：2019-03-27
"""

import time

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from work_box.define import *
from work_box.tools import getYaml, Device
from work_box.shell import ADB

class PaintArea(QWidget):
    def __init__(self):
        super(PaintArea,self).__init__()

        self._h = 720
        self._w = 450

        self.setPalette(QPalette(Qt.white))
        self.setAutoFillBackground(True)
        self.setFixedSize(self._h, self._w)
        self.image_path = ""
        self.pen = QPen(QColor('red'),3)

        self.start_flag = False
        self.end_flag = False

        self.start_point = None
        self.end_point = None

    def mousePressEvent(self, e):
        x = e.x()
        y = e.y()

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

        print("setImage", file_name)
        self.update()

    def paintEvent(self, QPaintEvent):
        p = QPainter(self)

        if self.image_path != "":
            print(self.image_path)
            pixmap = QPixmap(self.image_path)
            pixmap = pixmap.scaled(self._h, self._w, aspectRatioMode=Qt.KeepAspectRatio)
            p.drawPixmap(0, 0, pixmap)

        if self.start_point:
            p.setPen(QPen(QColor('red'),2))
            p.drawEllipse(self.start_point.x()-5, self.start_point.y()-5, 10,10)
        if self.end_point:
            p.setPen(QPen(QColor('blue'),2))
            p.drawEllipse(self.end_point.x()-5, self.end_point.y()-5, 10,10)

        if self.start_point and self.end_point:
            p.setPen(QPen(QColor('black'),3))
            p.drawLine(self.start_point, self.end_point)

class SwipPaintDialog(QDialog):
    def __init__(self, *args, **kw):
        super(SwipPaintDialog, self).__init__(*args, **kw)
        self.setWindowTitle('滑动图形')

        layout = QHBoxLayout()

        self.area = PaintArea()
        layout.addWidget(self.area)    

        item_layout = QVBoxLayout()
        button = QPushButton("截图")
        button.clicked.connect(self.screenshot)
        button.setFixedSize(150,30)
        item_layout.addWidget(button)

        start = QPushButton("起点")
        start.clicked.connect(self.start)
        start.setFixedSize(150,30)
        item_layout.addWidget(start)

        end = QPushButton("终端")
        end.clicked.connect(self.end)
        end.setFixedSize(150,30)
        item_layout.addWidget(end)

        item_layout.addStretch(1)

        buttonBox = QDialogButtonBox(parent=self)
        buttonBox.setOrientation(Qt.Horizontal)  # 设置为水平方向
        buttonBox.setStandardButtons(QDialogButtonBox.Ok)  # 确定和取消两个按钮
        buttonBox.accepted.connect(self.accept)  # 确定
        item_layout.addWidget(buttonBox)

        layout.addLayout(item_layout)
        self.setLayout(layout)

    def accept(self):
        if self.area.start_point and self.area.end_point:
            self.point = (self.area.start_point, self.area.end_point)
            super().accept()

    def start(self):
        self.area.start()

    def end(self):
        self.area.end()

    def screenshot(self):
        device = self.getDevoces()
        file_name = "%s.png" % time.strftime("%Y%m%d%H%M%S", time.localtime())

        adb = ADB(device)
        path = adb.screenshot(file_name)
        self.area.setImage(path)

    def getDevoces(self):
        devices = Device.get_android_devices()
        count = len(devices)

        if count == 0:
            print("没有连接设备")
            return
        elif count == 1:
            return devices[0]
        else:
            #TODO 多个设备选择一个
            pass

