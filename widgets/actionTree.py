
"""
@author: hyt
@time：2019-03-27
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# import qdarkstyle
from .issue import Issue
from .item import *

class ActionTree(QTreeView):
    def __init__(self, item = None):
        super().__init__()
        self.issue = Issue.get_init()
        self.copy_memory = []
        self.item = item
        
        self.setStyle()
        self.config()

    def setStyle(self):
        self.setMinimumWidth(100)
        # self.setSelectionMode(QAbstractItemView::ExtendedSelection)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        #设置拖拽模式
        self.setDragDropMode(QAbstractItemView.InternalMove)
        #设置是否可以编辑
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setStyleSheet("""
            QTreeView::item:selected {
                height: 25px;
                border: none;
                color: #CCCC33;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #333333, stop: 1 #444444);
            }

            QMenu {
                background-color: #333333; /* sets background of the menu */
                border: 1px solid black;
            }

            QMenu::item {
                /* sets background of menu item. set this to something non-transparent
                    if you want menu color and menu item color to be different */
                background-color: transparent;
            }

            QMenu::item:selected { /* when user selects item using mouse or keyboard */
                background-color: #654321;
            }

        """)    
    

    def config(self):
        #绑定点击事件
        self.clicked.connect(self.item_clicked)
        #右键菜单事件
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context)

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

    def item_clicked(self, index):
        item = self.__model.itemFromIndex(index)
        self.issue.send(Issue.SELECT_ITEM_VIEW, item)

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
        self.expandAll()

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

