
"""
@author: hyt
@time：2019-03-27
"""

import sys
import os
import time
import re

import xml.etree.cElementTree as ET
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from logger import set_logger
from work_box import *
from work_box.tools import Device
from work_box.shell import ADB
from .issue import Issue
from work_box.tools import parse_xml

@set_logger
class TiersList(QListWidget):
    def __init__(self, parent):
        super().__init__()
        self.issue = Issue.get_init()
        self.tiers_path = None
        self.index = 1
        self.parent = parent

        self.setStyle()
        self.config()
    
    def setStyle(self):
        self.setMinimumWidth(100)

    def config(self):
        """注册"""
        self.issue.reg(Issue.OPEN_SUITE, self.loadTiersFromSuite)
        self.itemClicked.connect(self.clicked)
        self.issue.reg(Issue.SCREENSHOT, self.screenshot)

    def screenshot(self):
        device = self.getDevoces()
        if self.tiers_path and device:
            time_name = "%s" % time.strftime("%Y%m%d%H%M%S", time.localtime())

            adb = ADB(device)
            QApplication.setOverrideCursor(Qt.WaitCursor)

            png_path = adb.screenshot(os.path.join(self.tiers_path, time_name+".png"))
            dump_path = adb.get_uidump(os.path.join(self.tiers_path, time_name+".xml"))

            if os.path.exists(png_path) and os.path.exists(dump_path):
                item = UIDumpItem(time_name, dump_path, png_path)
                self.addItem(item)
                self.setCurrentRow(self.row(item))
                self.clicked(item)

            QApplication.restoreOverrideCursor()

    def getDevoces(self):
        devices = Device.get_android_devices()
        count = len(devices)

        if count == 0:
            self.logger.error("没有连接设备")
            return None
        elif count == 1:
            return devices[0]
        else:
            #TODO 多个设备选择一个
            return devices[0]

    def loadTiersFromSuite(self, filename):
        self.clear()

        tiers_path = os.path.join(filename, "tiers")
        self.tiers_path = tiers_path
        if not os.path.exists(filename):
            self.logger.error("项目中 没有tiers文件夹")
            return

        tiers = []
        for path, folders, filenames in os.walk(tiers_path):
            for file_ in filenames:
                file_ = file_.replace(".png","")
                file_ = file_.replace(".xml","")

                if not file_ in tiers:
                    tiers.append(file_)
            break

        for tier in tiers:
            self.add_item(tier, tiers_path)

    def add_item(self, tier, filename):
        xml_path = os.path.join(filename, "".join([tier, ".xml"]))
        png_path = os.path.join(filename, "".join([tier, ".png"]))
        
        if os.path.exists(xml_path) and os.path.exists(png_path):
            item = UIDumpItem(tier, xml_path, png_path)
            self.addItem(item)

    def clicked(self, item):
        self.issue.send(Issue.CHANEG_TIER, item.dump, item.png_path)

    def contextMenuEvent(self, event):
        item = self.currentItem()
        if item:
            popMenu = QMenu(self)

            delete_action = QAction("删除", popMenu)
            delete_action.triggered.connect(lambda e,i=item: self.deleteDump(e,i))
            popMenu.addAction(delete_action)

            popMenu.exec_(QCursor.pos())
    
    def deleteDump(self, e, item):
        try:
            os.remove(item.dump_path)
            os.remove(item.png_path)
        except Exception:
            self.logger.exception("移除dump失败")
            return
        finally:
            self.takeItem(self.row(item)) 

class UIDumpItem(QListWidgetItem):
    def __init__(self, name, dump_path, png_path, size="1920x1600"):
        super().__init__(str(name))
        self.name = name
        self.dump = UIDump(dump_path)

        self.dump_path = dump_path
        self.png_path = png_path

        self.path, _ = os.path.split(dump_path)
        self.size = size

        self.setFlags(self.flags()| Qt.ItemIsEditable)

    def setData(self, role, value):
        if role == 2:
            new_dump_path = os.path.join(self.path, value+".xml")
            new_png_path = os.path.join(self.path, value+".png")
            try:
                os.rename(self.dump_path, new_dump_path)
                os.rename(self.png_path, new_png_path)
            except Exception:
                self.logger.exception("修改文件名出错")
                return
            finally:
                self.dump_path = new_dump_path
                self.png_path = new_png_path

        super().setData(role, value) 

class UIDump(object):
    def __init__(self, path):
        self.tree = ET.ElementTree(file=path)
        self.treeIter = self.tree.iter(tag="node")
        self.root = self.tree.getroot()
    
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