
"""
@author: hyt
@time：2019-03-27
"""

import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import qdarkstyle
from logger import set_logger
from work_box import *
from .tiersList import TiersList
from .dirTree import DirTree
from .actionTabView import ActionTabView
from .uiCatchPaintDialog import UICatchPaintDialog
from .showAttribStack import ShowAttribStacked
from .swipPaintDialog import SwipPaintDialog
from .issue import Issue
import xml.etree.cElementTree as ET

# issue = Issue.get_init()

@set_logger
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("动作用例编辑器")
        # self.logger = get_logger(self.__class__.__name__)

        self.issue = Issue.get_init()

        #创建工具栏
        self.tool_bar = QToolBar()

        #创建工具栏action
        self.new_sutie_action = QUnIcon("new_suite.png", "新建集合", self)
        # self.new_cml_action = QUnIcon("new_cml.png", "新建文件", self)
        self.open_action = QUnIcon("open.png", "打开", self)
        self.save_action = QUnIcon("save.png", "保存", self)
        # self.saveas_action = QUnIcon("saveas.png", "另存为", self)
        self.paly_action = QUnIcon("play.png", "播放", self)

        #工作桌
        self.worktable = WorkTable(self)
        
        self.setToolbarContents()
        self.setLayouts()
        self.setConnect()
        self.setStyle()
        # self.showMaximized()
        self.resize(1280, 800)

    def setStyle(self):
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())


    def setToolbarContents(self):
        """设置工具栏内容"""
        self.tool_bar.setIconSize(QSize(32, 32))

        self.tool_bar.addAction(self.new_sutie_action)
        # self.tool_bar.addSeparator()
        # self.tool_bar.addAction(self.new_cml_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.open_action)
        self.tool_bar.addAction(self.save_action)
        # self.tool_bar.addAction(self.saveas_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.paly_action)

    def setLayouts(self):
        """设置布局"""
        self.addToolBar(self.tool_bar)
        self.setCentralWidget(self.worktable)

    def setConnect(self):
        self.new_sutie_action.connect(self.get_suite_path)
        # self.new_cml_action.connect(self.creat_file)
        self.open_action.triggered.connect(self.open_file)
        self.save_action.triggered.connect(self.save)
        self.paly_action.triggered.connect(self.paly)

    def save(self):
        self.issue.send(Issue.SAVE_PROJECT)
        
    def paly(self):
        self.save()
        self.issue.send(Issue.PALY_PROJECT)

    # def creat_file(self):
    #     self.issue.send(Issue.CREAT_CML_FILE)

    def get_suite_path(self):
        dialog = CreatSuiteDialog()
        if dialog.exec_():
            if os.path.isabs(dialog.project_path):
                self.creat_suite(dialog.project_path)
    
    def creat_suite(self, suite_path):
        suite_path = suite_path+".suite"
        os.mkdir(suite_path)
        os.mkdir(os.path.join(suite_path, "case"))
        os.mkdir(os.path.join(suite_path, "tiers"))
        out_xml(self.creat_index_sml(), os.path.join(suite_path, "index.sml"))
        self.issue.send(Issue.OPEN_SUITE, suite_path)

    def creat_index_sml(self):
        root = ET.Element("root")
        node = ET.SubElement(root, "suite")
        node.attrib.update({
            "title": "用例集合"
        })

        return root

    def open_file(self):
        filename = QFileDialog.getExistingDirectory(self, "Open suite",
                                                CASE_PATH,
                                                QFileDialog.ShowDirsOnly)
        if filename:
            self.issue.send(Issue.OPEN_SUITE, filename)

@set_logger
class CreatSuiteDialog(QDialog):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.project_path = ""
        #路径地址
        self.path_edit = QLineEdit()
        self.path_button = QPushButton("...")
        self.suite_name_edit = QLineEdit()
        self.dialog_button_box = QDialogButtonBox(parent=self)

        self.setLayouts()
        self.setStyle()
        self.config()

    def setStyle(self):
        self.setWindowTitle('创建集合')
        self.path_edit.setText(CASE_PATH)
        self.dialog_button_box.setOrientation(Qt.Horizontal)
        self.dialog_button_box.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)

    def config(self):
        self.path_button.clicked.connect(self.get_path)
        self.dialog_button_box.accepted.connect(self.accept)
        self.dialog_button_box.rejected.connect(self.cancel)

    def setLayouts(self):
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.path_button)

        form_layout = QFormLayout()
        form_layout.addRow("路径地址", path_layout)
        form_layout.addRow("项目名称", self.suite_name_edit)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.dialog_button_box)

        self.setLayout(layout)
    
    def cancel(self):
        super().reject()

    def accept(self):
        path = self.path_edit.text()
        text = self.suite_name_edit.text()
        
        if path and text:
            self.project_path = os.path.join(path, text)
            super().accept()
        else:
            self.logger.info("项目信息未完善")

    def get_path(self):
        path = QFileDialog.getExistingDirectory(self, "Open suite",
                                                CASE_PATH,
                                                QFileDialog.ShowDirsOnly)
        if path:
            self.path_edit.setText(path)

class WorkTable(QSplitter):
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal)
        self.setChildrenCollapsible(False)
        self.setHandleWidth(1)

        self.parent = parent
        self.dirtree = DirTree()
        self.tiersList = TiersList(self)
        self.actionTabView = ActionTabView(self)
        # self.uiCatchPaintDialog = UICatchPaintDialog(self)
        self.showAttribStack = ShowAttribStacked(self)
        self.catchTabView = CatchTabView(self)

        self.setLayouts()
        self.setStyle()

    def setLayouts(self):
        left_splitter = QSplitter(Qt.Vertical)
        right_splitter = QSplitter(Qt.Vertical)

        self.addWidget(left_splitter)
        self.addWidget(self.actionTabView)
        self.addWidget(right_splitter)
        self.setChildrenCollapsible(False)
        self.setSizes([150,300,500])

        left_splitter.addWidget(self.dirtree)
        left_splitter.addWidget(self.tiersList)
        left_splitter.setChildrenCollapsible(False)
        left_splitter.setSizes([600,200])

        right_splitter.addWidget(self.showAttribStack)
        right_splitter.addWidget(self.catchTabView)
        right_splitter.setChildrenCollapsible(False)
        right_splitter.setSizes([300,500])

    def setStyle(self):
        pass
        self.dirtree.setStyleSheet('''
            QTreeWidgetItem{border:none;color:white;}
            ''')

class CatchTabView(QTabWidget):
    def __init__(self,parent = None):
        super().__init__(parent)

        self.uiCatchPaintDialog = UICatchPaintDialog(self)
        self.swipPaintDialog = SwipPaintDialog(self)
        self.setLayouts()
    def setLayouts(self):
        self.addTab(self.uiCatchPaintDialog, "取id")
        self.addTab(self.swipPaintDialog, "滑动")
        
class QUnIcon(QAction):
    def __init__(self, image_name = "action_define.png", action_name = "", parent=None):
        icon = QIcon(os.path.join(IMAGE_PATH, image_name))
        super().__init__(icon, action_name, parent)

    def connect(self, func):
        self.triggered.connect(func)


