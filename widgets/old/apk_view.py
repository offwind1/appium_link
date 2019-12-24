from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
import os
import re
import threading

from utility.shell import aapt
from utility.config import config
from utility.tools import Device
from utility.shell import ADB

class LabelEditer(QWidget):
    def __init__(self, tag,*args, **kw):
        super(LabelEditer, self).__init__(*args, **kw)
        self._tag = tag
        
        layout = QHBoxLayout()
        layout.setContentsMargins(1,1,1,1)

        self.label = QLabel(self)
        self.label.setText(self._tag)
        self.label.setFixedWidth(60)

        self.editer = QLineEdit(self)
        self.editer.setEnabled(False)

        layout.addWidget(self.label)
        layout.addWidget(self.editer)

        self.setLayout(layout)

    def setEditer(self,value):
        self.editer.setText(value)

    def update(self, data):
        self.setEditer(data.get(self._tag))

class ApkInfoView(QWidget):

    items = ["file_name","package","file_path","activity","version"]
    package_register = None

    def __init__(self, *args, **kw):
        super(ApkInfoView, self).__init__(*args, **kw)

        main_layout = QHBoxLayout()
        self.apk_button = QPushButton()
        self.apk_button.setIcon(QIcon(os.path.join("ico","android.png")))
        self.apk_button.setIconSize(QSize(100,100))
        self.apk_button.pressed.connect(self.__open_apk_file)
        self.apk_button.setStatusTip("选择apk文件")

        editer_layout = QVBoxLayout()

        self.editers = []
        for n ,val in enumerate(self.items):

            label_editer = LabelEditer(val)
            self.editers.append(label_editer)
            editer_layout.addWidget(label_editer)
        
        main_layout.addWidget(self.apk_button)
        main_layout.addLayout(editer_layout)

        self.setLayout(main_layout)

    def load(self):
        self.__load_apk_info(config.get_apk_path())

    def __open_apk_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file","",
                                                "app files (*.apk);;"
                                                "All files(*.*)")
        if filename:
            self.__load_apk_info(filename)
            config.set_apk_path(filename)

    def __load_apk_info(self, filename):
        path, filename = os.path.split(filename)

        aapt_appPackage = aapt.getApkPagename(filename)
        aapt_activity = aapt.getApkActivity(filename)

        appPackage =  re.findall("name=\'(.+?)\'",aapt_appPackage)[0] if aapt_appPackage else "没有，或查询失败"
        version = re.findall("versionName=\'(.+?)\'",aapt_appPackage)[0] if aapt_appPackage else "没有，或查询失败"
        activity = re.findall("name=\'(.+?)\'",aapt_activity)[0] if aapt_activity else "没有，或查询失败"

        data = dict(zip(self.items,[filename, appPackage, path, activity, version]))
        self.__update_editer(data)

        if self.package_register:
            self.package_register.load(appPackage)

    def __update_editer(self,data):
        for editer in self.editers:
            editer.update(data)

    def add_package_register(self,register):
        self.package_register = register

class ButtonDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(ButtonDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index):
            button = QPushButton(
                self.tr('更新'),
                self.parent(),
                clicked=self.parent().cellButtonClicked
            )

            button.index = [index.row(), index.column()]

            h_box_layout = QHBoxLayout()
            h_box_layout.addWidget(button)
            h_box_layout.setContentsMargins(0, 0, 0, 0)
            h_box_layout.setAlignment(Qt.AlignCenter)

            widget = QWidget()
            widget.setLayout(h_box_layout)
            self.parent().setIndexWidget(
                index,
                widget
            )

class ProgressBarDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(ProgressBarDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        # if not self.parent().indexWidget(index):
        if index.column() == 3:
            value = index.model().data(index, Qt.DisplayRole)

            # progressBarOption = QStyleOptionProgressBar()

            widget = QWidget()
            
            pro_bar = QStyleOptionProgressBar()
            pro_bar.maximum = 100
            pro_bar.minimum = 0
            pro_bar.textAlignment = Qt.AlignCenter
            pro_bar.progress = value

            # pro_bar = QProgressBar(widget)
            pro_bar.rect = option.rect.adjusted(4, 4, -4, -4)
            # pro_bar.setMinimum(0)
            # pro_bar.setMaximum(100)
            # pro_bar.setAlignment(Qt.AlignCenter)
            # pro_bar.setValue(value)

            painter.save()
            if (option.state & QStyle.State_Selected):
                painter.fillRect(option.rect, option.palette.highlight())
                painter.setBrush(option.palette.highlightedText())

            QApplication.style().drawControl(QStyle.CE_ProgressBar, pro_bar, painter)
            painter.restore()


            
            # h_box_layout = QHBoxLayout()
            # h_box_layout.addWidget(pro_bar)
            # h_box_layout.setAlignment(Qt.AlignCenter)

            # widget.setLayout(h_box_layout)
            # self.parent().setIndexWidget(
            #     index,
            #     widget
            # )

class MyModel(QAbstractTableModel):
    """item_list=[
            [packagename, √ or x, "安装"],
            [packagename, √ or x, "安装"]
        ]
    """
    item_list = []
    headers = ["package","是否安装","操作","进度条"]

    def __init__(self, parent=None):
        super(MyModel, self).__init__(parent)

    def load(self,package):
        self.item_list.clear()

        """device_info = [packagename, √ or x, "安装"]"""
        for device in Device.get_android_devices():
            device_info = []
            device_info.append(device)

            value = '√' if ADB(device).get_matching_app_list(package) else 'x'

            device_info.append(value)
            device_info.append("安装")
            device_info.append(10)

            self.item_list.append(device_info)

    def rowCount(self, QModelIndex):
        return len(self.item_list)

    def columnCount(self, QModelIndex):
        return len(self.headers)

    def headerData(self,section,orientation,role=Qt.DisplayRole):
        # 实现标题行的定义
        if role != Qt.DisplayRole:
            return None
 
        if orientation == Qt.Horizontal:
            return self.headers[section]
        return int(section + 1)

    def data(self, index, role):
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole:
            return self.item_list[row][col]
        return QVariant()

    def get_value(self,r,c):
        return self.item_list[r][c]

class MyTableView(QTableView):

    table_model = None
    button_delegate = None
    progressBar_delegate = None

    def __init__(self, parent=None):
        super(MyTableView, self).__init__(parent)

        self.table_model = MyModel()
        self.button_delegate = ButtonDelegate(self)
        self.progressBar_delegate= ProgressBarDelegate(self)

        self.setModel(self.table_model)

        self.setItemDelegateForColumn(2, self.button_delegate)
        self.setItemDelegateForColumn(3, self.progressBar_delegate)

        self.horizontalHeader().setStretchLastSection(True)

    def cellButtonClicked(self):
        r , c = self.sender().index
        device = self.model().get_value(r,0)

        s = self.table_model.item_list[r]
        
        try:
            t = threading.Thread(target=self.aaa,args=(device, s,))
            t.start()
        except Exception as e:
            raise e

    def aaa(self, device, s):
        print(device , s)
        ADB(device).install_app(config.get_apk_path(), lambda v,s=s: self.pr(v,s))

    def pr(self, value, s):
        p = re.findall("\[\s?(.+?)%\]",value)
        print(p)
        if len(p)>0:
            s[3] = int(p[0])
            self.table_model.layoutChanged.emit()

    def load(self,package):
        self.model().load(package)
        self.update()

class ApkView(QWidget):
    """APK界面"""
    def __init__(self, *args, **kw):
        super(ApkView, self).__init__(*args, **kw)

        main_layout = QVBoxLayout() #主要layout

        apk_info = ApkInfoView()    #apk信息界面
        tableView = MyTableView()   #创建tableView

        #apk，绑定 tableView
        apk_info.add_package_register(tableView)
        apk_info.load()

        #配置Layout
        main_layout.addWidget(apk_info)
        main_layout.addWidget(tableView)
        main_layout.setContentsMargins(5,5,5,5)
        self.setLayout(main_layout)
