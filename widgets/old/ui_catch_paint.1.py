from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utility.define import *
from utility.tools import parse_xml
from utility.tools import Device
from utility.shell import ADB

import xml.etree.cElementTree as ET
import time
import re

class PaintArea(QWidget):
    def __init__(self, parent):
        super(PaintArea,self).__init__()
        self._parent = parent
        self._w = 720
        self._h = 450
        self._width = self._w
        self._height = self._h

        self.line_bounds = None
        self.UIDump = None  

        self.setPalette(QPalette(Qt.white))
        self.setAutoFillBackground(True)
        self.setFixedSize(self._w, self._h)
        self.image_path = ""
        self.pen = QPen(QColor('red'),2)


    def setUIDump(self, dump):
        self.UIDump = dump

    def setDeviceSize(self, str):
        [size] = re.findall(": (\d+)x(\d+)", str)
        width, height = size
        self._width = int(width)
        self._height = int(height)

    def mousePressEvent(self, e):
        if self.UIDump:
            x = (e.x()/self._w)*self._width
            y = (e.y()/self._h)*self._height

            item = self.UIDump.find_item_by_pos((x,y))
            if item is not None:
                self.line_bounds = item.attrib["bounds"]
                self._parent.show_item_attrib(item)
                self.update()

    def setImage(self, file_name):
        self.image_path = file_name
        self.update()

    def paintEvent(self, QPaintEvent):
        p = QPainter(self)
        p.setPen(self.pen)

        if self.image_path != "":
            pixmap = QPixmap(self.image_path)
            pixmap = pixmap.scaled(self._w, self._h, aspectRatioMode=Qt.KeepAspectRatio)
            p.drawPixmap(0, 0, pixmap)

        if self.line_bounds:
            [bounds] = re.findall("\\[(.+?),(.+?)\\]\\[(.+?),(.+?)\\]", self.line_bounds)
            a, b, c, d = bounds
            item_lx = int(a)
            item_ly = int(b)
            item_rx = int(c)
            item_ry = int(d)
            
            x_scale = self._w/self._width
            y_scale = self._h/self._height

            x = item_lx * x_scale
            y = item_ly * y_scale
            w = (item_rx - item_lx) * x_scale
            h = (item_ry - item_ly) * y_scale

            rect = QRect(x,y,w,h) 
            p.drawRect(rect)

class UIDump(object):
    def __init__(self, path):
        self.tree = ET.ElementTree(file=path)
        self.treeIter = self.tree.iter(tag="node")

    def find_item_by_text(self, text):
        item_list = []
        for item in self.treeIter:
            if item.attrib["text"]:
                continue
            if item.attrib["text"]==text:
                item_list.append(item)

        return item_list

    def find_item_by_pos(self, pos):
        x,y = pos
        temp_lx , temp_ly, temp_rx, temp_ry = 0, 0, 5000, 5000
        find_item = None

        for item in self.tree.iter(tag="node"):
            [bounds] = re.findall("\\[(.+?),(.+?)\\]\\[(.+?),(.+?)\\]", item.attrib["bounds"])
            a, b, c, d = bounds
            item_lx = int(a)
            item_ly = int(b)
            item_rx = int(c)
            item_ry = int(d)

            if x > item_lx and x < item_rx and y > item_ly and y < item_ry:
                if (item_lx>=temp_lx and item_ly >= temp_ly) and (item_rx <= temp_rx and item_ry <= temp_ry):
                    temp_lx , temp_ly, temp_rx, temp_ry = item_lx, item_ly, item_rx, item_ry
                    find_item = item

        return find_item

class UICatchPaintDialog(QDialog):
    def __init__(self, *args, **kw):
        super(UICatchPaintDialog, self).__init__(*args, **kw)
        self.setWindowTitle('UICatch')

        layout = QHBoxLayout()

        self.area = PaintArea(self)
        layout.addWidget(self.area)    

        item_layout = QVBoxLayout()
        button = QPushButton("截图")
        button.clicked.connect(self.screenshot)
        button.setFixedSize(150,30)
        item_layout.addWidget(button)

        item_layout.addStretch(1)

        self.label_text = QLabel("text:")
        self.label_id = QLabel("resource-id:")
        item_layout.addWidget(self.label_text)
        item_layout.addWidget(self.label_id)

        item_layout.addStretch(1)

        buttonBox = QDialogButtonBox(parent=self)
        buttonBox.setOrientation(Qt.Horizontal)  # 设置为水平方向
        buttonBox.setStandardButtons(QDialogButtonBox.Ok)  # 确定和取消两个按钮
        buttonBox.accepted.connect(self.accept)  # 确定
        item_layout.addWidget(buttonBox)

        layout.addLayout(item_layout)

        self.setLayout(layout)

    def show_item_attrib(self, item):
        attrib = item.attrib
        self.label_text.setText("text:{}".format(attrib.get("text")))
        self.label_id.setText("resource-id:{}".format(attrib.get("resource-id")))

    def accept(self):
        super().accept()

    def screenshot(self):
        device = self.getDevoces()
        file_name = "%s.png" % time.strftime("%Y%m%d%H%M%S", time.localtime())

        adb = ADB(device)
        QApplication.setOverrideCursor(Qt.WaitCursor)

        self.area.setImage(adb.screenshot(file_name))
        self.area.setUIDump(UIDump(adb.get_uidump()))
        self.area.setDeviceSize(adb.get_size())
        QApplication.restoreOverrideCursor()

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
