import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utility.define import *
from gui_qt.actionItem import *
from utility.tools import out_xml, parse_xml
from gui_qt.ui_catch_paint import UICatchPaintDialog
from gui_qt.welcome_view import WelcomeView

# from gui_qt.actionItem.baseItem import *


class MyModel(QStandardItemModel):
    def __init__(self,*args,**kw):
        super(MyModel, self).__init__(*args,**kw)
        self.init_attrib()
        self.init()
    
    def init_attrib(self):
        self.main_item = MainTitleItem()
        self.insertRow(0, self.main_item)
        self.temp_items = [] #拖拽的item临时存储空间

    def init(self):
        item = QStandardItem(QIcon(os.path.join(IMAGE_PATH,"editor.png")),"编辑区")
        self.setHorizontalHeaderItem(0,item)

    def flags(self, index):
        flags = QAbstractItemModel.flags(self, index)
        flags = flags | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        return flags

    def mimeData(self, indexes):
        #用户尝试拖拽操作（拖动鼠标）时调用
        if len(indexes) <= 0: #若用户没有选中item，不执行
            return 0

        self.temp_items.clear() #清除临时存储空间
        data = QMimeData()      #生成 QMimeData

        for indexe in indexes:
            item = self.itemFromIndex(indexe) #获取index位置（选中的）的item

            #判断是否可以拖拽
            if not item.state & ItemState.CAN_DRAG:
                return 

            # temp_item = self.get_no_perfect_chone(item)
            # self.temp_items.append(temp_item)

            self.temp_items.append(item) #将该item存入临时存储空间
            data.setData("drag",b"2")    #生成QMimeData 定义 drag
        
        return data #执行mimeTypes函数，若data非drag，则不能拖拽

    def get_no_perfect_chone(self, item):
        #仅生产了新的item，item的view没有重新生产
        temp_item = item.copy()

        if item.hasChildren():
            i = 0
            while item.child(i):
                child = item.child(i)

                temp_child = self.get_no_perfect_chone(child)
                temp_item.setChild(i, temp_child)

                i += 1

        return temp_item

    def get_perfect_chone(self, item):
        #item的view是重新生产的
        temp_item = item.clone()

        if item.hasChildren():
            i = 0
            while item.child(i):
                child = item.child(i)

                temp_child = self.get_perfect_chone(child)
                temp_item.setChild(i, temp_child)

                i += 1

        return temp_item

    def dropMimeData(self, minidata, action, row, column, parent):
        #执行拖拽时，"放开"的操作
        item = self.itemFromIndex(parent) #获取"放开"的位置上的item
        if item == None:    #若放开位置上没有item，则不执行操作
            return False 

        if item.state & ItemState.CAN_INCLUDE: #判断放开位置上的item，能否包含
            #拖拽插入
            for temp_item in self.temp_items:  #变量临时存储中的item
                
                #生成 item的克隆（仅生成新的item，view是现有的）
                temp_item = self.get_no_perfect_chone(temp_item)

                if row == -1:
                    item.appendRow(temp_item)   #插入到末尾
                else:
                    item.insertRow(row, temp_item) #插入到row位置
            return True
        return False

    def mimeTypes(self):
        #判断mimedata的允许拖拽的类型
        return ["drag"]

    def get_xml(self):
        #将model变成xml格式文件存储，返回root
        root = ET.Element("root")
        self.get_item_xml(self.main_item, root)
        return root

    def get_item_xml(self, parent, root):
        #遍历parent下的所有children，生成xml树
        parent_node = parent.save_to_xml(root)

        if parent.hasChildren():
            i = 0
            while parent.child(i):
                child = parent.child(i)
                self.get_item_xml(child, parent_node)
                i += 1

    def load_from_xml(self, root):
        #从xml文件读取数据，生成model树
        if not root.tag == "root":
            raise Exception("文件不正确")

        self.clear()    #清理model
        self.init()     

        for main in root:
            item_name = KEY_DICT[main.tag]
            self.main_item = item_name()
            self.appendRow(self.main_item)

            self.main_item.load_from_xml(main)
            self.temp(self.main_item, main)

    def temp(self, parent, root):
        for node in root:
            if node.tag in KEY_DICT:
                item_name = KEY_DICT[node.tag]
                item = item_name()
                item.load_from_xml(node)

                parent.appendRow(item)

                self.temp(item, node)

class SutieModel(MyModel):
    def __init__(self, *args, **kw):
        super(SutieModel, self).__init__(*args,**kw)

    def init_attrib(self):
        self.main_item = MainSuiteItem()
        self.insertRow(0, self.main_item)
        self.temp_items = [] #拖拽的item临时存储空间

class ActionTree(QTreeView):
    stacked_view = None

    def __init__(self, parent=None):
        super(ActionTree, self).__init__(parent)
        self.copy_memory = []
        self.setMinimumWidth(100)

        self.__model = MyModel(self)
        self.setModel(self.__model)
        # self.setSelectionMode(QAbstractItemView::ExtendedSelection)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        #右键菜单事件
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context)

        #设置拖拽模式
        self.setDragDropMode(QAbstractItemView.InternalMove)
        #设置是否可以编辑
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #绑定点击事件
        self.clicked.connect(self.item_clicked)

        self.ITEM_LIST = ITEM_LIST

    def new_cml_file(self):
        self.__model = MyModel(self)
        self.setModel(self.__model)
        self.ITEM_LIST = ITEM_LIST
    
    def new_suite_file(self):
        self.__model = SutieModel(self)
        self.setModel(self.__model)
        self.ITEM_LIST = SUITE_LIST

    def mousePressEvent(self, event):
        """重载鼠标点击事件，点击空白处取消选中"""
        index = self.indexAt(event.pos())
        if index.row() == -1:
            self.setCurrentIndex(index)
        else:
            super().mousePressEvent(event)

    def set_stacked_view(self, stacked_view):
        self.stacked_view = stacked_view

    def item_clicked(self, index):
        item = self.__model.itemFromIndex(index)
        try:
            temp_view = self.stacked_view.currentWidget()
            if temp_view:
                self.stacked_view.removeWidget(temp_view)
            self.stacked_view.addWidget(item.view)
            self.stacked_view.setCurrentWidget(item.view)
        except Exception as e:
            print(e)

    def show_context(self):
        indexs = self.selectedIndexes()

        if not len(indexs):
            indexs.append(self.__model.indexFromItem(self.__model.main_item))

        if len(indexs) == 1:
            self.onlyone_menu(indexs[0])
        else:
            self.multiple_menu()

    def multiple_menu(self):
        popMenu = QMenu(self)

        delete_action = QAction("删除", popMenu)
        delete_action.triggered.connect(self.delete_multiple_item)
        popMenu.addAction(delete_action)

        copy_action = QAction("复制", popMenu)
        copy_action.triggered.connect(self.copy_multiple_item)
        popMenu.addAction(copy_action)

        popMenu.addSeparator()

        stop_action = QAction("禁用", popMenu)
        stop_action.triggered.connect(self.stop_multiple_item)
        popMenu.addAction(stop_action)

        start_action = QAction("启用", popMenu)
        start_action.triggered.connect(self.start_multiple_item)
        popMenu.addAction(start_action)

        popMenu.exec_(QCursor.pos())

    def get_selected_indexes(self):
        indexs = self.selectedIndexes()
        i = 0
        for index in indexs:
            item = self.__model.itemFromIndex(index)
            if item == self.__model.main_item:
                indexs.pop(i)
            i+=1
        return indexs

    def delete_multiple_item(self, event):
        while self.get_selected_indexes():
            index = self.get_selected_indexes()[0]
            self.__model.removeRow(index.row(), index.parent())

    def copy_multiple_item(self, event):
        indexs = self.get_selected_indexes()
        self.copy_memory.clear()

        for index in indexs:
            item = self.__model.itemFromIndex(index)
            self.copy_memory.append(item)

    def stop_multiple_item(self, event):
        indexs = self.get_selected_indexes()
        for index in indexs:
            item = self.__model.itemFromIndex(index)
            item.set_online(False)
    
    def start_multiple_item(self, event):
        indexs = self.get_selected_indexes()
        for index in indexs:
            item = self.__model.itemFromIndex(index)
            item.set_online(True)

    def onlyone_menu(self, index):
        popMenu = QMenu(self)
        item = self.__model.itemFromIndex(index)
        if item.menu & ItemState.MENU_DELETE:    
            #删除菜单
            delete_action = QAction("删除", popMenu)
            delete_action.triggered.connect(lambda e,i=index:self.delete_item(e, i))
            popMenu.addAction(delete_action)

        if item.menu & ItemState.MENU_COPY:
            #复制菜单
            copy_action = QAction("复制", popMenu)
            copy_action.triggered.connect(lambda e,i=item:self.copy_item(e,i))
            popMenu.addAction(copy_action)
            
        if item.menu & ItemState.MENU_PASTE:
            #黏贴菜单
            paste_action = QAction("粘贴", popMenu)
            paste_action.triggered.connect(lambda e,i=item:self.paste_item(e,i))
            popMenu.addAction(paste_action)

        popMenu.addSeparator()

        annotation_action = QAction(item.online and "禁用" or "启用", popMenu)
        annotation_action.triggered.connect(lambda e,i=item:self.annotation_item(e,i))
        popMenu.addAction(annotation_action)

        popMenu.addSeparator()

        if item.menu & ItemState.MENU_ACTION:
            for group in self.ITEM_LIST:
                for key in group:
                    menu = QMenu(key,popMenu)
                    popMenu.addMenu(menu)
                    for _class in group[key]:
                        action = QAction(_class.name, self)
                        action.triggered.connect(lambda e,i=index,s=_class: self.add_click_action(e,i,s))
                        menu.addAction(action)
           
        popMenu.exec_(QCursor.pos())

    def show_context2(self):
        index = self.currentIndex()

        if not index.isValid():
            index = self.__model.indexFromItem(self.__model.main_item)

        item = self.__model.itemFromIndex(index)
        popMenu = QMenu(self)

        if item.menu & ItemState.MENU_DELETE:    
            #删除菜单
            delete_action = QAction("删除", popMenu)
            delete_action.triggered.connect(lambda e,i=index:self.delete_item(e, i))
            popMenu.addAction(delete_action)

        if item.menu & ItemState.MENU_COPY:
            #复制菜单
            copy_action = QAction("复制", popMenu)
            copy_action.triggered.connect(lambda e,i=item:self.copy_item(e,i))
            popMenu.addAction(copy_action)
            
        if item.menu & ItemState.MENU_PASTE:
            #黏贴菜单
            paste_action = QAction("粘贴", popMenu)
            paste_action.triggered.connect(lambda e,i=item:self.paste_item(e,i))
            popMenu.addAction(paste_action)

        popMenu.addSeparator()

        if item.menu & ItemState.MENU_ACTION:
            for group in self.ITEM_LIST:
                for key in group:
                    menu = QMenu(key,popMenu)
                    popMenu.addMenu(menu)
                    for _class in group[key]:
                        action = QAction(_class.name, self)
                        action.triggered.connect(lambda e,i=index,s=_class: self.add_click_action(e,i,s))
                        menu.addAction(action)
           
        popMenu.exec_(QCursor.pos())
    
    def paste_item(self, event, item):
        #粘贴
        if self.copy_memory:
            for copy_item in self.copy_memory:
                temp = self.__model.get_perfect_chone(copy_item)
                if item:
                    item.appendRow(temp)
                else:
                    self.__model.main_item.appendRow(temp)

    def copy_item(self, event, item):
        self.copy_memory.clear()
        self.copy_memory.append(item)

    def annotation_item(self, event, item):
        #删除
        item.change_online()

    def delete_item(self, event, index):
        #删除
        parent_index = index.parent()
        parent = self.__model.itemFromIndex(parent_index)
        parent.takeRow(index.row())

    def add_click_action(self, event, index, standard_item):
        #添加动作。逻辑。或变量
        item = standard_item()

        if index.isValid():
            partent = self.__model.itemFromIndex(index)
            partent.appendRow(item)
            self.setExpanded(index,True)
            self.setCurrentIndex(item.index())
            self.item_clicked(item.index())
        else:
            self.__model.appendRow(item)

    def keyPressEvent(self, e):
        #按键响应
        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_C:
            #复制
            index = self.currentIndex()
            item = self.__model.itemFromIndex(index)
            if item.menu & ItemState.MENU_COPY:
                self.copy_item("",item)
        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_V:
            index = self.currentIndex()
            item = self.__model.itemFromIndex(index)
            if item:
                if item.menu & ItemState.MENU_PASTE:
                    self.paste_item("",item)
            else:
                self.paste_item("",item)

    def save_to_xml(self):
        return self.__model.get_xml()
    
    def load_from_xml(self, root):
        for main in root:
            pass

        if main.tag == "main":
            self.new_cml_file()
        elif main.tag == "suite" or main.tag == "sutie":
            self.new_suite_file()

        self.__model.load_from_xml(root)

class ActionEditor(QMainWindow):
    CASE = ".cml"
    SUITE = ".suite"

    def __init__(self,*args,**kw):
        super(ActionEditor, self).__init__(*args,**kw)
        self.setWindowTitle("动作用例编辑器")
        self.resize(QSize(800,600))
        

        self.editor_type = ActionEditor.CASE
        
        self.file_name = None

        #主布局
        layout = QHBoxLayout()

        #==工具栏
        tool_bar = QToolBar()
        tool_bar.setIconSize(QSize(32,32))

        new_cml_icon = QIcon(os.path.join(IMAGE_PATH,"new_cml.png"))
        new_cml_action = QAction(new_cml_icon,"新建CML",self)
        new_cml_action.triggered.connect(self.new_cml_file)
        tool_bar.addAction(new_cml_action)

        new_suite_icon = QIcon(os.path.join(IMAGE_PATH,"new_suite.png"))
        new_suite_action = QAction(new_suite_icon,"新建集合",self)
        new_suite_action.triggered.connect(self.new_suite_file)
        tool_bar.addAction(new_suite_action)

        tool_bar.addSeparator()

        open_icon = QIcon(os.path.join(IMAGE_PATH,"open.png"))
        open_action = QAction(open_icon,"打开",self)
        open_action.triggered.connect(self.open_from_xml)
        tool_bar.addAction(open_action)

        save_icon = QIcon(os.path.join(IMAGE_PATH,"save.png"))
        save_action = QAction(save_icon,"保存",self)
        save_action.triggered.connect(self.save_to_xml)
        tool_bar.addAction(save_action)

        saveas_icon = QIcon(os.path.join(IMAGE_PATH,"saveas.png"))
        saveas_action = QAction(saveas_icon,"另存为",self)
        saveas_action.triggered.connect(self.saveas_to_xml)
        tool_bar.addAction(saveas_action)

        tool_bar.addSeparator()

        paly_icon = QIcon(os.path.join(IMAGE_PATH,"play.png"))
        paly_action = QAction(paly_icon,"播放",self)
        paly_action.triggered.connect(self.play)
        tool_bar.addAction(paly_action)

        #界面分割器
        splitter = QSplitter(Qt.Horizontal)     
        #界面不能被分割为0
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(1)

        self.action_tree = ActionTree()
        splitter.addWidget(self.action_tree)

        self.stacked_view = QStackedWidget()
        self.action_tree.set_stacked_view(self.stacked_view)
        self.stacked_view.addWidget(WelcomeView())

        splitter.addWidget(self.stacked_view)

        splitter.insertWidget(0, UICatchPaintDialog(self)) 

        splitter.setSizes([200, 200, 200])
        # splitter.setStretchFactor(1,1)
        splitter.setStretchFactor(2,0)

        layout.addWidget(splitter)
        # self.setLayout(layout)

        widget = QWidget()
        widget.setLayout(layout)

        # palette = QPalette()
        # palette.setColor(widget.backgroundRole(), QColor(51,51,51))
        # widget.setPalette(palette)
        # widget.setAutoFillBackground(True)


        self.addToolBar(tool_bar)
        self.setCentralWidget(widget)

        self.showMaximized()

    def load_item_info(self, data):
        if self.action_tree.selectedIndexes():
            view = self.stacked_view.currentWidget()
            if view:
                if hasattr(view, "synchron"):
                    view.synchron(data)

    def new_cml_file(self):
        self.action_tree.new_cml_file()
        self.file_name = None
        self.editor_type = ActionEditor.CASE

    def new_suite_file(self):
        self.action_tree.new_suite_file()
        self.file_name = None
        self.editor_type = ActionEditor.SUITE

    def open_from_xml(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file","",
                                                "case files (*.cml *.suite);;"
                                                "All files(*.*)")
        if filename:
            self.file_name = filename

            if ".cml" in filename:
                self.editor_type = ActionEditor.CASE
            elif ".suite" in filename:
                self.editor_type = ActionEditor.SUITE

            root = parse_xml(filename)
            self.action_tree.load_from_xml(root)
        
    def save_to_xml(self):
        if self.file_name is None:
            self.saveas_to_xml()
            return
        else:
            root = self.action_tree.save_to_xml()
            out_xml(root, self.file_name)

    def saveas_to_xml(self):
        filename, _ = QFileDialog.getSaveFileName(self, "保存文件", "",
                                                "app files (*{});;All files(*.*)".format(self.editor_type))
        if filename:
            self.file_name = filename
            self.save_to_xml()

    def play(self):
        self.save_to_xml()
        if self.file_name:
            p = Process(target=start_run_device,args=(self.file_name,))
            p.start()

def start_run_device(file_name):
    from core.testAdmin import TestAdmin
    # run_device(file_name)
    TestAdmin(file_name)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    casemana = ActionEditor()
    casemana.show()

    sys.exit(app.exec_())