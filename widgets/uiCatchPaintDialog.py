"""
@author: hyt
@time：2019-03-27
"""

import time
import re

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import xml.etree.cElementTree as ET

from work_box import *
from work_box.tools import Device

from logger import set_logger
from .issue import Issue


@set_logger
class PaintArea(QFrame):
    def __init__(self, parent):
        super(PaintArea, self).__init__()
        self._parent = parent
        self.line_bounds = None
        self.UIDump = None
        self.image_path = ""
        self.pen = QPen(QColor('red'), 2)

        self.search_text = ""
        self.item_list = []
        self.search_index = 0
        self.next_func = None

        self._w = self.size().width()
        self._h = self.size().height()
        self._width = self._w
        self._height = self._h
        self._s = 0

        self.setStyle()

    def setStyle(self):
        self.setPalette(QPalette(Qt.white))
        self.setAutoFillBackground(True)
        # self.setMinimumSize(360, 640)
        self.setContentsMargins(0, 0, 0, 0)

    def get_item(self):
        i = 0
        while True:
            if self.item_list:
                length = len(self.item_list)
                i = i % (length)
                yield self.item_list[i]
                i += 1
            else:
                yield None

    def search(self, search_text):
        if self.UIDump:
            if search_text != self.search_text:
                self.search_text = search_text
                self.item_list = self.UIDump.find_item_by_text(search_text)
                self.next_func = self.get_item()

            if self.next_func:
                item = next(self.next_func)

                if item is not None:
                    self.line_bounds = item.attrib["bounds"]
                    self._parent.show_item_attrib(item)
                    self.update()

    def setUIDump(self, dump):
        self.UIDump = dump

    def mousePressEvent(self, e):
        if self.UIDump:
            print(self._w, self._width, e.x())
            # x = (e.x() / self._w) * self._width
            x = e.x() * self._s
            # y = (e.y() / self._h) * self._height
            y = e.y() * self._s

            item = self.UIDump.updateSelectionForCoordinates((x, y))
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

        self._w, self._h = self.size().width(), self.size().height()
        # if self._w < self._h:
        #     self._w, self._h = self._h, self._w

        if os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)

            h = pixmap.height()
            w = pixmap.width()

            x = self._h if self._h < self._w else self._w
            z = h if h > w else w
            self._s = z / x
            temp_pixmap = pixmap.scaled(x, x, aspectRatioMode=Qt.KeepAspectRatio)
            p.drawPixmap(0, 0, temp_pixmap)

            self._width = temp_pixmap.width()
            self._height = temp_pixmap.height()

            if self.line_bounds:
                [bounds] = re.findall("\\[(.+?),(.+?)\\]\\[(.+?),(.+?)\\]", self.line_bounds)
                a, b, c, d = bounds
                item_lx = int(a)
                item_ly = int(b)
                item_rx = int(c)
                item_ry = int(d)

                # x_scale = self._w/self._width
                x_scale = temp_pixmap.width() / pixmap.width()
                # y_scale = self._h/self._height
                y_scale = temp_pixmap.height() / pixmap.height()

                x = item_lx * x_scale
                y = item_ly * y_scale
                w = (item_rx - item_lx) * x_scale
                h = (item_ry - item_ly) * y_scale

                rect = QRect(x, y, w, h)
                p.drawRect(rect)


@set_logger
class UICatchPaintDialog(QFrame):
    def __init__(self, parent):
        super(UICatchPaintDialog, self).__init__()
        # self.setWindowTitle('UICatch')
        # self.resize(QSize(720,600))
        self.issue = Issue.get_init()
        self._parent = parent
        self.mem_item = None

        # 搜索栏
        self.search_edit = QLineEdit()
        # 搜索按钮
        self.search_button = QPushButton("搜索")
        # 画板
        self.area = PaintArea(self)
        # 截图按钮
        self.shotcut_button = QPushButton("截图")
        # 属性Table
        self.table_view = QTableWidget()

        button_list_info = [("获取ID", "id", "resource-id"),
                            ("获取Class", "class name", "class"),
                            ("获取text", "name", "text")]

        self.item_button_list = []

        for titel, typ, value in button_list_info:
            button = QPushButton(titel)
            button.clicked.connect(lambda i, t=typ, v=value: self.update_item_info(t, v))
            button.setFixedSize(150, 30)
            self.item_button_list.append(button)

        self.setLayouts()
        self.setStyle()
        self.config()

    def setLayouts(self):
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_button)

        item_layout = QVBoxLayout()
        item_layout.addWidget(self.shotcut_button)
        # item_layout.addStretch(1)
        for button in self.item_button_list:
            item_layout.addWidget(button)

        separator_layout = QHBoxLayout()
        separator_layout.addLayout(item_layout)
        separator_layout.addWidget(self.table_view)

        layout = QVBoxLayout()

        layout.addLayout(search_layout)
        layout.addWidget(self.area)
        layout.addLayout(separator_layout)

        self.setLayout(layout)

    def setStyle(self):
        # self.setMaximumWidth(740)
        self.setFrameShape(QFrame.StyledPanel)

        self.shotcut_button.setFixedSize(150, 30)

        self.table_view.setColumnCount(2)
        self.table_view.horizontalHeader().resizeSection(0, 100)
        self.table_view.horizontalHeader().resizeSection(1, 400)
        self.table_view.setHorizontalHeaderLabels(["type", "value"])
        self.table_view.setMaximumHeight(150)

    def config(self):
        self.search_button.clicked.connect(self.search)
        self.shotcut_button.clicked.connect(self.screenshot)
        self.issue.reg(Issue.CHANEG_TIER, self.show_item)

    def show_item_attrib(self, item):
        self.mem_item = item
        self.table_view.setRowCount(len(item.attrib))
        i = 0
        for key in item.attrib:
            key_item = QTableWidgetItem(key)
            value_item = QTableWidgetItem(item.attrib.get(key))

            self.table_view.setItem(i, 0, key_item)
            self.table_view.setItem(i, 1, value_item)
            i += 1

    def search(self):
        search_text = self.search_edit.text()
        self.area.search(search_text)

    def update_item_info(self, typ, value):
        if self.mem_item is not None:
            attrib = self.mem_item.attrib
            self.issue.send(Issue.SEND_ELEMENT_ID, {
                "value": attrib.get(value),
                "type": typ,
                "name": attrib.get("text")
            })

    def show_item(self, dump, png_path):
        self.area.setUIDump(dump)
        self.area.setImage(png_path)

    def screenshot(self):
        self.issue.send(Issue.SCREENSHOT)
