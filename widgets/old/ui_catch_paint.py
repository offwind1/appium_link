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

class PaintArea(QFrame):
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

        self.search_text = ""
        self.item_list = []
        self.search_index = 0
        self.next_func = None

    def get_item(self):
        i = 0
        while True:
            if self.item_list:
                length = len(self.item_list)
                i = i%(length)
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

    def setDeviceSize(self, str):
        [size] = re.findall(": (\d+)x(\d+)", str)
        width, height = size
        self._width = int(width)
        self._height = int(height)

    def mousePressEvent(self, e):
        if self.UIDump:
            x = (e.x()/self._w)*self._width
            y = (e.y()/self._h)*self._height

            # item = self.UIDump.find_item_by_pos((x,y))
            item = self.UIDump.updateSelectionForCoordinates((x,y))
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
            if pixmap.width() > pixmap.height():
                self.setFixedSize(self._w, self._h)
                pixmap = pixmap.scaled(self._w, self._h, aspectRatioMode=Qt.KeepAspectRatio)
            else:
                self.setFixedSize(self._h, self._w)
                pixmap = pixmap.scaled(self._h, self._w,aspectRatioMode=Qt.KeepAspectRatio)
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

class IFindNodeListener(object):
    def __init__(self):
        self.mNode = None
        self.x = None
        self.y = None
        self.width = None
        self.height =None

    def onFoundNode(self, node,x,y,width,height) :
        if self.mNode == None:
            self.mNode = node
            self.x = x
            self.y = y
            self.width = width
            self.height = height
        else :
            if (height * width) < (self.height * self.width):
                self.mNode = node
                self.x = x
                self.y = y
                self.width = width
                self.height = height
                
class UIDump(object):
    def __init__(self, path):
        self.tree = ET.ElementTree(file=path)
        self.treeIter = self.tree.iter(tag="node")

        self.root = self.tree.getroot()
        # self.b(self.root)
    
    def get_bounds(self, node):
        bounds = re.findall("\\[-?(\\d+),-?(\\d+)\\]\\[-?(\\d+),-?(\\d+)\\]", node.attrib.get("bounds"))
        a, b, c, d = bounds[0]
        x = int(a)
        y = int(b)
        width = int(c) - x
        height = int(d) - y

        return x,y,width,height

    def find_item_by_text(self, text):
        item_list = []
        for item in self.tree.iter(tag="node"):
            if item.attrib["text"]:

                if text in item.attrib["text"]:
                    item_list.append(item)
        return item_list

    def updateSelectionForCoordinates(self, pos):
        x,y = pos
        node = None
        lister = IFindNodeListener()
        found = self.findLeafMostNodesAtPoint(x, y, lister, self.root);
        if found and lister.mNode != None:
            node = lister.mNode

        return node;

    def findLeafMostNodesAtPoint(self, px, py, lister, root):
        foundInChild = False
        for node in root:
            foundInChild |= self.findLeafMostNodesAtPoint(px, py, lister,node)

        if foundInChild:
            return True;

        if root.attrib.get("bounds"):
            x,y,width,height = self.get_bounds(root)
        
            if x <= px and px <= (x + width) and y <= py and py <= (y + height):
                lister.onFoundNode(root, x,y,width,height)
                return True
        
        return False

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

class UIDumpItem(QListWidgetItem):
    def __init__(self, name, dump, sh_path, size):
        super(UIDumpItem, self).__init__(str(name))
        self.dump = dump
        self.sh_path = sh_path
        self.size = size
        self.setFlags(self.flags()| Qt.ItemIsEditable)

class UIDumpListWidget(QListWidget):
    def __init__(self, parent):
        super(UIDumpListWidget, self).__init__()
        self.setFixedWidth(70)
        
        self.index = 1
        self._parent = parent

    def add_item(self, dump, sh_path, size):
        item = UIDumpItem(self.index, dump, sh_path, size)
        self.addItem(item)
        self.index+=1

        return item

    def clicked(self, item, item_):
        self._parent.show_item(item)
        # QMessageBox.information(self, "ListWidget", "你选择了: " + item.sh_path)

class UICatchPaintDialog(QFrame):
    def __init__(self, parent):
        super(UICatchPaintDialog, self).__init__()
        # self.setWindowTitle('UICatch')
        # self.resize(QSize(720,600))
        self._parent = parent
        self.setMaximumWidth(740)
        self.setFrameShape(QFrame.StyledPanel)

        self.mem_item = None
        layout = QVBoxLayout()

        search_layout = QHBoxLayout()

        self.search_edit = QLineEdit()
        search_button = QPushButton("搜索")
        search_button.clicked.connect(self.search)

        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_button)

        layout.addLayout(search_layout)

        #画板
        self.area = PaintArea(self)
        layout.addWidget(self.area)    

        separator_layout = QHBoxLayout()
        layout.addLayout(separator_layout)

        item_layout = QVBoxLayout()
        separator_layout.addLayout(item_layout)
        #截图按钮
        shotcut_button = QPushButton("截图")
        shotcut_button.clicked.connect(self.screenshot)
        shotcut_button.setFixedSize(150,30)
        item_layout.addWidget(shotcut_button)
        
        ###################

        item_layout.addStretch(1)

        button_list_info = [("获取ID","id","resource-id"),
                            ("获取Class","class name","class"),
                            ("获取text","name","text")]
        for titel, typ, value in button_list_info:
            update_Class_button = QPushButton(titel)
            update_Class_button.clicked.connect(lambda i,t=typ,v=value:self.update_item_info(t,v))
            update_Class_button.setFixedSize(150,30)
            item_layout.addWidget(update_Class_button)
        
        #表单
        self.table_view = QTableWidget()
        self.table_view.setColumnCount(2)
        self.table_view.horizontalHeader().resizeSection(0,100)
        self.table_view.horizontalHeader().resizeSection(1,400)
        self.table_view.setHorizontalHeaderLabels(["type","value"])
        # self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
    
        separator_layout.addWidget(self.table_view)

        self.dump_list_view = UIDumpListWidget(self)
        # self.dump_list_view.itemClicked.connect(self.dump_list_view.clicked)
        self.dump_list_view.currentItemChanged.connect(self.dump_list_view.clicked)
        separator_layout.addWidget(self.dump_list_view)

        self.setLayout(layout)

    def show_item_attrib(self, item):
        self.mem_item = item
        self.table_view.setRowCount(len(item.attrib))
        i = 0
        for key in item.attrib:
            key_item = QTableWidgetItem(key) 
            value_item = QTableWidgetItem(item.attrib.get(key)) 

            self.table_view.setItem(i, 0, key_item)  
            self.table_view.setItem(i, 1, value_item)
            i+=1

    def search(self):
        search_text = self.search_edit.text()
        self.area.search(search_text)

    def update_item_info(self, typ, value):
        if self.mem_item is not None:
            attrib = self.mem_item.attrib
            self._parent.load_item_info({
                "value":attrib.get(value),
                "type":typ,
                "name":attrib.get("text")
            })

    def show_item(self, item):
        self.area.setImage(item.sh_path)
        self.area.setUIDump(item.dump)
        self.area.setDeviceSize(item.size)

    def screenshot(self):
        device = self.getDevoces()
        if device:
            file_name = "%s.png" % time.strftime("%Y%m%d%H%M%S", time.localtime())

            adb = ADB(device)
            QApplication.setOverrideCursor(Qt.WaitCursor)

            sh_path = adb.screenshot(file_name)
            dump = UIDump(adb.get_uidump())
            size = adb.get_size()

            item = self.dump_list_view.add_item(dump, sh_path, size)
            self.dump_list_view.setCurrentItem(item)

            QApplication.restoreOverrideCursor()

    def getDevoces(self):
        devices = Device.get_android_devices()
        count = len(devices)

        if count == 0:
            print("没有连接设备")
            return None
        elif count == 1:
            return devices[0]
        else:
            #TODO 多个设备选择一个
            return devices[0]
