
"""
@author: hyt
@time：2019-03-27
"""

import sys
import os
import shutil

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from multiprocessing import Process

from logger import set_logger
from work_box import *
from .issue import Issue
from work_box.tools import parse_xml
from .actionTree import ActionTree
import xml.etree.cElementTree as ET
from core.project import Project

@set_logger
class FileItem(QTreeWidgetItem):
    FOLDER = "FOLDER"
    FILE = "FILE"

    def __init__(self, parent, item_name, file_path, type):
        super().__init__(parent)
        self.view = None
        self.type = type
        self.file_path = file_path
        self.name = item_name
        self.issue = Issue.get_init()

        self.setFlags(self.flags()|Qt.ItemIsEditable)
        self.setItemName(item_name)
        self.creatView()

        if type == self.FOLDER:
            self.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        
    def saveSelfToFile(self):
        if self.view:#and self.type is self.FILE:
            root = self.view.save_to_xml()
            out_xml(root, self.get_path())

    def creatView(self):
        if os.path.isfile(self.file_path):
            self.view = ActionTree(self)
            if self.file_path.endswith('.sml'):
                self.view.new_suite_file()
            elif self.file_path.endswith('.cml'):
                self.view.new_cml_file()
            try:
                self.view.load_from_xml(parse_xml(self.file_path))
            except Exception as e:
                self.logger.exception("初始化view出错")

    def setItemName(self, item_name):
        self.setText(0, item_name)
        if self.type == self.FOLDER:
            self.setIcon(0, QIcon(os.path.join(IMAGE_PATH, "folder.png")))
        elif self.type == self.FILE:
            self.setIcon(0, QIcon(os.path.join(IMAGE_PATH, "file.png")))
    
    def setData(self, column, role, value):
        if role == 2:
            old_path = self.get_path()
            new_path = old_path.replace(self.name, value)
            try:
                os.rename(old_path, new_path)
                self.name = value
                self.issue.send(Issue.CHANGE_TAB_NAME, self, value)
            except Exception:
                self.logger.exception("修改文件名出错")
                return
        super().setData(column, role, value)

    def get_path(self):
        parent = self.parent()
        if parent:
            parent_path = parent.get_path()
            return os.path.join(parent_path, self.name)

class TitleItem(QTreeWidgetItem):
    def __init__(self, parent, item_name, index_file):
        super().__init__(parent)
        self.view = None
        self.type = FileItem.FOLDER
        self.index_file = index_file
        self.project_path = os.path.join(os.path.join(self.index_file, os.pardir), "case")

        self.setText(0, item_name)
        self.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        self.creatView()

    def get_path(self):
        return self.project_path

    def saveSelfToFile(self):
        if self.view:
            root = self.view.save_to_xml()
            out_xml(root, self.index_file)

    def creatView(self):
        if os.path.isfile(self.index_file):
            self.view = ActionTree(self)
            self.view.new_suite_file()
            try:
                self.view.load_from_xml(parse_xml(self.index_file))
            except Exception as e:
                self.logger.exception("初始化view出错")

@set_logger
class DirTree(QTreeWidget):
    def __init__(self, worktable=None):
        super().__init__(worktable)
        self.mainItem = None
        self.issue = Issue.get_init()
        self.main_path = None

        self.config()
        self.setStyle()

    def setStyle(self):
        self.setItemsExpandable(True)
        self.header().hide()
        self.setIndentation(10)
        self.setMinimumWidth(100)

    def config(self):
        """注册"""
        self.itemClicked.connect(self.click)
        self.issue.reg(Issue.OPEN_SUITE, self.openSuiteToCreatTree)
        # self.issue.reg(Issue.CREAT_CML_FILE, self.creatCmlFile)
        self.issue.reg(Issue.SAVE_PROJECT, self.save_project)
        self.issue.reg(Issue.PALY_PROJECT, self.paly)

    def paly(self):
        if self.mainItem and self.main_path:
            p = Process(target=start_run_device,args=(self.mainItem.index_file, self.mainItem.project_path))
            p.start()
        else:
            self.logger.error("mainItem , main_path 为空")

    def save_project(self):
        if self.mainItem:
            self.loop_save(self.mainItem)

    def loop_save(self, root):
        childCount = root.childCount()
        if childCount > 0:
            for i in range(childCount):
                node = root.child(i)
                self.loop_save(node)
        root.saveSelfToFile()

    def creatCmlFile(self):
        items = self.selectedItems()
        if items and self.main_path:
            [item] = items
            parent = item.parent()
            
            if item.type is FileItem.FOLDER:
                if item is self.mainItem:
                    path = os.path.join(self.main_path,"case")
                    new_file_name, new_file_path = self.creat_new_cml(path)
                else:
                    new_file_name, new_file_path = self.creat_new_cml(item.file_path)
                FileItem(item, new_file_name, new_file_path, FileItem.FILE)
            elif item.type is FileItem.FILE:
                if item is self.mainItem or parent is self.mainItem:
                    path = os.path.join(self.main_path,"case")
                    new_file_name, new_file_path = self.creat_new_cml(path)
                    FileItem(self.mainItem, new_file_name, new_file_path, FileItem.FILE)
                else:
                    new_file_name, new_file_path = self.creat_new_cml(parent.file_path)
                    FileItem(parent, new_file_name, new_file_path, FileItem.FILE)
        
    def creat_new_cml(self, parent_path):
        temp_file_name = "新建文件.cml"
        temp_file_path = os.path.join(parent_path, temp_file_name)

        index = 0
        while os.path.exists(temp_file_path):
            index += 1
            temp_file_name = "新建文件"+"-"+str(index)+".cml"
            temp_file_path = os.path.join(parent_path, temp_file_name)

        try:
            out_xml(self.creat_root(), temp_file_path)
        except Exception:
            self.logger.exception("创建文件时错误")

        return temp_file_name, temp_file_path

    def creat_root(self):
        root = ET.Element("root")
        node = ET.SubElement(root, "main")
        node.attrib.update({
            "online":"True",
            "title":"用例进程"
        })
        return root

    def click(self, item, index):
        if item.view is not None :
            self.issue.send(Issue.CREAT_TAB, item)

    def openSuiteToCreatTree(self, main_path):
        self.clear()
        self.main_path = main_path
        Project.setProject(self.main_path)
        self.mainItem = self.creatMainItemFromIndexFile(os.path.join(main_path, "index.sml"), main_path)

        if self.mainItem:
            self.creatChildFileItem(main_path)

        self.expandAll()

    def creatMainItemFromIndexFile(self, index_path, filename):
        """读取index文件，创建mainitem"""
        if not os.path.exists(index_path):
            self.logger.error("项目中 没有index.sml文件")
            return None

        path, project_name = os.path.split(filename)
        item = TitleItem(self, project_name, index_path)
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        return item

    def creatChildFileItem(self, main_path):
        """读取case文件夹，创建文件树"""
        case_path = os.path.join(main_path, "case")
        if not os.path.exists(case_path):
            self.logger.error("项目中 没有case文件夹")
            return
        self.creatTree(case_path, self.mainItem)

    def creatTree(self, case_path, root):
        for path, folders, filenames in os.walk(case_path):
            for folder in folders:
                folder_path = os.path.join(path, folder)
                folder_item = FileItem(root, folder, folder_path, FileItem.FOLDER)
                folder_item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                self.creatTree(folder_path, folder_item)

            for filename in filenames:
                if filename.endswith('.cml'):
                    case_file = os.path.join(path,filename)
                    file_item = FileItem(root, filename, case_file, FileItem.FILE)
            break
    
    def creatFolderItem(self):
        if self.main_path:
            item = self.currentItem()
            parent = item.parent()

            if item.type is FileItem.FOLDER:
                if item is self.mainItem:
                    path = os.path.join(self.main_path,"case")
                    new_folder_name, new_folder_path = self.creatFolder(path)
                else:
                    new_folder_name, new_folder_path = self.creatFolder(item.file_path)

                item.insertChild(0, FileItem(None, new_folder_name, new_folder_path, FileItem.FOLDER))
            elif item.type is FileItem.FILE:
                if item is self.mainItem or parent is self.mainItem:
                    path = os.path.join(self.main_path,"case")
                    new_folder_name, new_folder_path = self.creatFolder(path)
                    self.mainItem.insertChild(0, FileItem(None, new_folder_name, new_folder_path, FileItem.FOLDER))
                else:
                    new_folder_name, new_folder_path = self.creatFolder(parent.file_path)
                    parent.insertChild(0, FileItem(None, new_folder_name, new_folder_path, FileItem.FOLDER))

    def creatFolder(self, parent_path):
        temp_folder_name = "新建文件夹"
        temp_folder_path = os.path.join(parent_path, temp_folder_name)

        index = 0
        while os.path.exists(temp_folder_path):
            index += 1
            temp_folder_name = "新建文件夹"+"-"+str(index)
            temp_folder_path = os.path.join(parent_path, temp_folder_name)

        try:
            os.mkdir(temp_folder_path)
        except Exception:
            self.logger.exception("创建文件夹时错误")

        return temp_folder_name, temp_folder_path

    def deleteFile(self):
        item = self.currentItem()
        try:
            path = item.file_path
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)
        except Exception:
            self.logger.exception("删除文件失败")
            return

        parent = item.parent()
        parent.removeChild(item)

    def contextMenuEvent(self, event):
        item = self.currentItem()
        if item:
            popMenu = QMenu(self)

            new_file_action = QAction("新建文件", popMenu)
            new_file_action.triggered.connect(self.creatCmlFile)
            popMenu.addAction(new_file_action)

            new_folder = QAction("新建文件夹", popMenu)
            new_folder.triggered.connect(self.creatFolderItem)
            popMenu.addAction(new_folder)

            if item is not self.mainItem:
                popMenu.addSeparator()

                delete_action = QAction("删除", popMenu)
                delete_action.triggered.connect(self.deleteFile)
                popMenu.addAction(delete_action)

                if item.type is FileItem.FILE:
                    popMenu.addSeparator()

                    play_action = QAction("执行", popMenu)
                    play_action.triggered.connect(lambda e,i=item:self.paly_cml(i))
                    popMenu.addAction(play_action)
            
            popMenu.exec_(QCursor.pos())
        
    def paly_cml(self, item):
        self.save_project()
        if self.mainItem and self.main_path:
            index_path = item.get_path()
            p = Process(target=start_run_cml, args=(index_path, 
                                            self.mainItem.project_path, 
                                            self.mainItem.index_file))
            p.start()
        else:
            self.logger.error("mainItem , main_path 为空")

def start_run_device(file_name, project_path):
    from core.testAdmin import TestAdmin
    TestAdmin(file_name, project_path)

def start_run_cml(file_name, project_path, index_file):
    from core.testAdmin import TestAdmin, APKInfo
    TestAdmin(file_name, project_path, APKInfo(index_file))