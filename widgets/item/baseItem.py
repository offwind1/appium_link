
"""
@author: hyt
@time：2019-03-27
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import re

# from gui_tk.CassMange import CassMange
from multiprocessing import Process, queues
import xml.etree.cElementTree as ET

from work_box.define import *
from work_box.shell import aapt
# from gui_qt.pageWidget import PageWidget
from work_box.tools import *

ACTION = "action"
LOGIC = "logic"
VALUE = "value"
MAIN = "main"

def open_page_window(func):
    window = CassMange(func)
    window.mainloop()

class LabelEditer(QWidget):
    def __init__(self, tag, *args, **kw):
        super(LabelEditer, self).__init__(*args, **kw)
        self._tag = tag
        
        layout = QHBoxLayout()
        layout.setContentsMargins(1,1,1,1)

        self.label = QLabel(self)
        self.label.setText(APK_INFO_VIEW_TABLE[self._tag])
        # self.label.setFixedWidth(60)

        self.editer = QLineEdit(self)
        # self.editer.setEnabled(False)
        self.editer.setReadOnly(True)

        layout.addWidget(self.label)
        layout.addWidget(self.editer)

        self.setLayout(layout)

    def setEditer(self, value):
        self.editer.setText(str(value))

    def update(self, data):
        self.setEditer(data.get(self._tag))

    def get_value(self):
        return {self._tag : self.editer.text()}

class ApkInfoView(QWidget):
    items = ["apklabel","package","version","file_path"]

    def __init__(self, *args, **kw):
        super(ApkInfoView, self).__init__(*args, **kw)
        self.data = {}

        main_layout = QHBoxLayout()
        self.apk_button = QPushButton()
        self.apk_button.setIcon(QIcon(os.path.join(IMAGE_PATH,"android.png")))
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

    # def load(self):
    #     self.__load_apk_info(config.get_apk_path())

    def __open_apk_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open file","",
                                                "app files (*.apk);;"
                                                "All files(*.*)")
        if file_path:
            self.__load_apk_info(file_path)

    def __load_apk_info(self, file_path):
        path, filename = os.path.split(file_path)

        aapt_appPackage = aapt.getApkPagename(file_path)
        # aapt_activity = aapt.getApkActivity(file_path)
        aapt_apklabel = aapt.getApkName(file_path)

        apklabel = re.findall("application-label:\'(.+?)\'",aapt_apklabel)[0] if aapt_appPackage else "没有，或查询失败"
        appPackage =  re.findall("name=\'(.+?)\'",aapt_appPackage)[0] if aapt_appPackage else "没有，或查询失败"
        version = re.findall("versionName=\'(.+?)\'",aapt_appPackage)[0] if aapt_appPackage else "没有，或查询失败"
        # activity = re.findall("name=\'(.+?)\'",aapt_activity)[0] if aapt_activity else "没有，或查询失败"

        self.data = dict(zip(self.items,[apklabel, appPackage, version, file_path]))
        self.__update_editer(self.data)

    def __update_editer(self, data):
        for editer in self.editers:
            editer.update(data)

    def self_to_data(self, data):
        data.update(self.data)

    def update(self, data):
        self.__update_editer(data)

    def self_to_xml(self, node):
        data = {}
        for editer in self.editers:
            s = editer.get_value()
            data.update(s)

        node.attrib.update(data)
        return node
    
    def xml_to_data(self, node):
        return node.attrib

class ValueTableView(QWidget):
    def __init__(self, tag = "value",*args, **kw):
        super(ValueTableView, self).__init__(*args,**kw)
        layout = QVBoxLayout(self)

        self.tag = tag
        #表单
        self.table_view = QTableWidget()
        self.table_view.setColumnCount(2)
        self.table_view.horizontalHeader().resizeSection(0,150)
        self.table_view.horizontalHeader().resizeSection(1,200)
        self.table_view.setHorizontalHeaderLabels(["name","value"])
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout.addWidget(self.table_view)

        #按钮组
        button_layout = QHBoxLayout()
        add_button = QPushButton("添加", self)
        add_button.clicked.connect(self.add_row)

        delete_button = QPushButton("删除", self)
        delete_button.clicked.connect(self.delete_row)

        button_layout.addWidget(add_button)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def delete_row(self):
        row = self.table_view.currentRow()
        if row is not -1:
            self.table_view.removeRow(row)

    def add_row(self):
        self.table_view.setRowCount(self.table_view.rowCount()+1)

    def self_to_data(self, data):
        rows = self.table_view.rowCount()

        data["value_list"] = []
        for rows_index in range(rows):
            name_item = self.table_view.item(rows_index,0)
            if name_item:
                name = name_item.text()
            else:
                name = ""

            value_item = self.table_view.item(rows_index,1)
            if value_item:
                value = value_item.text()
            else:
                value = ""

            data["value_list"].append({name:value})

    def update(self, data):
        row = len(data["value_list"])
        self.table_view.setRowCount(row)

        for index in range(row):

            for key in data["value_list"][index]:
                name = key
                value = data["value_list"][index][key]
                
                name_Item = QTableWidgetItem(name)  
                value_item = QTableWidgetItem(value) 

                self.table_view.setItem(index, 0, name_Item)  
                self.table_view.setItem(index, 1, value_item)

    def self_to_xml(self, node, data):
        for value in data["value_list"]:
            for key in value:
                value_node = ET.SubElement(node, self.tag)
                value_node.attrib.update({"name":key})
                value_node.text = value[key]
        return node

    def xml_to_data(self, root):
        data = {}
        data["value_list"] = []
        for value in root:
            if value.tag == self.tag:
                key = value.attrib["name"]
                val = value.text
                data["value_list"].append({key:val})
        return data

class ValueTableView2(ValueTableView):
    def self_to_data(self, data):
        rows = self.table_view.rowCount()

        data["value_list"] = []
        for rows_index in range(rows):
            name_item = self.table_view.item(rows_index,0)
            if name_item:
                name = name_item.text()
            else:
                name = ""

            value_item = self.table_view.item(rows_index,1)
            if value_item:
                value = value_item.text()
            else:
                value = ""

            # data["value_list"].append({name:value})
            data["value_list"].append({
                "name":name,
                "value":value,
                "title":"设置变量"
            })

    def update(self, data):
        row = len(data["value_list"])
        self.table_view.setRowCount(row)

        for index in range(row):
            item_data = data["value_list"][index]
            name = item_data.get("name")
            value = item_data.get("value")

            name_Item = QTableWidgetItem(name)  
            value_item = QTableWidgetItem(value)

            self.table_view.setItem(index, 0, name_Item)  
            self.table_view.setItem(index, 1, value_item)
    
    def self_to_xml(self, node, data):
        for item_data in data["value_list"]:
            name = item_data.get("name")
            value = item_data.get("value")

            value_node = ET.SubElement(node, self.tag)
            value_node.attrib.update({
                "name":name,
                "value":value,
                "title":"设置变量"
            })
        return node

    def xml_to_data(self, root):
        data = {}
        data["value_list"] = []
        for item_node in root:
            if item_node.tag == "value_p" or item_node.tag == "value":
                data["value_list"].append(item_node.attrib)
        return data

class ItemSelectWidget(QFrame):
    def __init__(self, parent):
        super(ItemSelectWidget, self).__init__()
        self.data = {}
        self._parent = parent
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("控件属性:", self))

        #表单
        form_layout = QFormLayout()
        self.type_edit = QLineEdit(self)
        self.value_edit = QLineEdit(self)
        form_layout.addRow("type:", self.type_edit)
        form_layout.addRow("value:", self.value_edit)

        layout.addLayout(form_layout)

        self.setLayout(layout)
        self.setFrameShape(QFrame.Box)

    def self_to_data(self, data):
        self.data = {
            "type":self.type_edit.text(),
            "value":self.value_edit.text()
        }

        data.update(self.data)
    
    def load_from_page(self, page):
        self.data = page
        self.update()#更新 page editer
        if page.get("name"):
            self._parent.set_title_edit(self._parent.item.name+":"+page.get("name"))

    def update(self):
        self.type_edit.setText(self.data.get("type"))
        self.value_edit.setText(self.data.get("value"))

class PageSelectWidget(QWidget):
    def __init__(self, *args, **kw):
        super(PageSelectWidget, self).__init__(*args,**kw)
        self.data = {}
        self.name = ""
        self.type = ""
        self.value = ""
        
        try:
            self.widget = args[0]
        except Exception as e:
            print(e)
            self.widget = None

        layout = QHBoxLayout()

        self.editer = QLineEdit(self)
        self.editer.setReadOnly(True)
        # self.editer.setFixedSize(200,30)

        self.button = QPushButton("选择page", self)
        # self.button.setFixedSize(150,30)
        self.button.clicked.connect(self.get_page_loc)

        layout.addWidget(self.editer)
        layout.addWidget(self.button)
        layout.addStretch(1)
        
        self.setLayout(layout)

    def self_to_data(self, data):
        data.update(self.data)

    def load_from_page(self, page):
        self.data = page
        self.update()#更新 page editer
        
        self.widget.set_title_edit(self.widget.item.name+":"+page.get("name"))

    def get_page(self):
        return self.page, self.element

    def update(self):
        self.editer.setText("{}: {}".format(self.data.get("page"),self.data.get("name")))

    def get_page_loc(self):
        dialog = PageWidget()
        if dialog.exec_():
            self.load_from_page(dialog.page)

class TitelWidget(QWidget):
    def __init__(self, *args, **kw):
        super(TitelWidget, self).__init__(*args,**kw)

        layout = QBoxLayout(QBoxLayout.LeftToRight)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setFont(QFont("Roman times",15,QFont.Bold))

        layout.addWidget(self.label)
        self.setLayout(layout)

        # self.set_background()

    def set_background(self):
        pe = self.palette()
        pe.setColor(QPalette.Background, Qt.blue)
        self.setAutoFillBackground(True)
        self.setPalette(pe)
        self.show()

    def set_title(self, text):
        self.label.setText(text)

class BaseWidget(QFrame):
    """
        重载\n
        update 从字典更新界面\n
        xml_to_data 将xml文件转换成data字典\n
        self_to_data 将自己变成data字典\n
        self_to_xml 将自己变成xml
    """
    key = "none"

    def __init__(self, item):
        super(BaseWidget, self).__init__()
        self.setMinimumWidth(100)
        self.setFrameShape(QFrame.StyledPanel)
        self.data = {}
        self.item = item

        layout = QVBoxLayout(self)

        self.title_widget = TitelWidget(self)
        self.title_widget.set_title(self.item.name)
        layout.addWidget(self.title_widget)

        self.title_edit = QLineEdit()
        self.title_edit.setText(self.item.text())
        self.title_edit.editingFinished.connect(
            lambda: self.item.setText(self.title_edit.text())
        )

        form_layout = QFormLayout()
        form_layout.addRow("标题:", self.title_edit)
        layout.addLayout(form_layout)

        self.setLayout(layout)

    def set_title_edit(self, title):
        self.title_edit.setText(title)
        self.item.setText(title)

    def get_title(self):
        return self.title_edit.text()

    def load_from_data(self, data):
        # print(self.key, data)
        self.update(data)

    def update(self,data):
        pass

    def load_from_xml(self, root):
        self.title_edit.setText(self.item.text())
        data = self.xml_to_data(root)
        self.load_from_data(data)

    def xml_to_data(self, root):
        # print(self.key, root.attrib)
        return root.attrib

    def save_to_data(self):
        self.data.clear()
        self.self_to_data()

    def self_to_data(self):
        pass

    def save_to_xml(self, root, online = True):
        node = ET.SubElement(root, self.key)
        node.attrib.update({
            "title": self.get_title(),
            "online": str(online)
        })
        self.save_to_data()
        self.self_to_xml(node)
        return node
    
    def self_to_xml(self, root):
        pass

    def get_data(self):
        self.save_to_data()
        return self.data
    
    def clone(self, item):
        temp = self.__class__(item)
        temp.load_from_data(self.get_data())
        return temp

class ItemState:
    CAN_DRAG =      0b00000001 #可以拖拽
    CONNOT_DRAG =   0b00000010  #不可以拖拽    
    CAN_INCLUDE=    0b00000100  #可以包容
    CONNOT_INCLUDE =0b00001000 #不可以包容
    MENU_DELETE =   0b00010000 #菜单有删除
    MENU_COPY =     0b00100000 #菜单有复制
    MENU_PASTE =    0b01000000 #菜单有黏贴
    MENU_ACTION =   0b10000000 #菜单有动作项目

class BaseItem(QStandardItem):
    name = "没有设置name"
    state = ItemState.CONNOT_DRAG | ItemState.CONNOT_INCLUDE
    menu = ItemState.MENU_ACTION

    def __init__(self,qicon):#*args,**kw):
        super(BaseItem, self).__init__(qicon,self.name)#*args,**kw)
        self.view = BaseWidget(self)
        self.online = True
        self.online_brush = QBrush(Qt.white, Qt.SolidPattern)
        self.offline_brush = QBrush(Qt.gray, Qt.SolidPattern)
        # self.setProperty("online", True);
        self.setForeground(self.online_brush)
        
    def set_online(self, online):
        if online is not None:
            if isinstance(online, str):
                online = online.lower()
                if online.lower() == "false":
                    online = False
                elif online.lower() == "true":
                    online = True

            if isinstance(online, bool):
                self.online = online
                self.item_update()

    def change_online(self):
        self.online = not self.online
        self.item_update()

    def item_update(self):
        if self.online:
            self.setForeground(self.online_brush)
        else:
            self.setForeground(self.offline_brush)

    def clone(self):
        #克隆自己，包括view也新生成
        temp = self.__class__()
        temp.setText(self.text())
        temp.view = self.view.clone(temp)
        return temp

    def copy(self):
        #仅克隆自身，view复制指针，没有新生成
        temp = self.__class__()
        temp.setText(self.text())
        temp.view = self.view
        temp.view.item = temp
        return temp

    def save_to_xml(self, root):
        return self.view.save_to_xml(root, self.online)

    def load_from_xml(self, root):
        data = root.attrib
        self.setText(data["title"])
        self.set_online(data.get("online"))
        self.view.load_from_xml(root)

