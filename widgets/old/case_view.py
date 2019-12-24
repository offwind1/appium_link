from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import os

# from utility.define import BIN_DIR_PATH, BIN_DIR_NAME, BIN_FILE_TAG

def listUp(l,index):
    if index ==0:
        return FALSE
    l.insert(index-1,l.pop(index))
    return l

def listDown(l,index):
    if index == len(l):
        return FALSE
    l.insert(index+1,l.pop(index))
    return l

class ListModel(QStringListModel):
    def __init__(self, *args, **kw):
        super(ListModel, self).__init__(*args, **kw)
        self.list = []
        current_path = QDir.currentPath()
        self.sutie_path = os.path.join(current_path, BIN_DIR_PATH.CASE)

    def add_file(self, file_path):
        path = os.path.join(self.sutie_path, file_path)

        if os.path.isfile(path):
            if BIN_FILE_TAG.CASE in path:
                self.list.append(file_path)
        else:
            for dir_path, dir_names, file_names in os.walk(path):
                for file_name in file_names:
                    if BIN_FILE_TAG.CASE in file_name:
                        path_name = os.path.join(dir_path, file_name)
                        temp_path = os.path.join(self.sutie_path,"")
                        self.list.append(path_name.replace(temp_path,""))

        self.setStringList(self.list)

    def remove_file(self, index):
        self.list.pop(index.row())
        self.setStringList(self.list)

    def up_file(self, index):
        listUp(self.list, index.row())
        self.setStringList(self.list)

    def down_file(self, index):
        listDown(self.list, index.row())
        self.setStringList(self.list)

class ListView(QListView):
    def __init__(self, *args, **kw):
        super(ListView, self).__init__(*args, **kw)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested[QPoint].connect(self.show_context)

    def show_context(self, point):
        index = self.currentIndex()
        print(index)
        if index.isValid():
            popMenu = QMenu()
            up_action = QAction(u'上移', self)
            down_action = QAction(u'下移', self)

            up_action.triggered.connect(lambda b,i=index:self.up_file(b,i))
            down_action.triggered.connect(lambda b,i=index:self.down_file(b,i))

            popMenu.addAction(up_action)
            popMenu.addAction(down_action)

            popMenu.exec_(QCursor.pos())

    def up_file(self, bool,index):
        self.model().up_file(index)

    def down_file(self, bool, index):
        self.model().down_file(index)

class ListWidget(QWidget):
    _top = None
    def __init__(self, top, *args, **kw):
        super(ListWidget, self).__init__(*args, **kw)
        self._top = top

        list_layout = QVBoxLayout(self)

        self.list_model = ListModel()
        self.list_view = ListView()
        self.list_view.setModel(self.list_model)

        remove_button = QPushButton("remove")
        remove_button.clicked.connect(self.remove_file)

        list_layout.addWidget(self.list_view)
        list_layout.addWidget(remove_button)

    def remove_file(self):
        index = self.list_view.currentIndex()
        print(index, index.data())
        self.list_model.remove_file(index)

    def add_file(self, file_path):
        self.list_model.add_file(file_path)

class TreeView(QWidget):
    _top = None
    def __init__(self, top, *args, **kw):
        super(TreeView, self).__init__(*args, **kw)

        self._top = top

        #定位路径
        current_path = QDir.currentPath()
        sutie_path = os.path.join(current_path, BIN_DIR_PATH.CASE)

        #主布局
        tree_layout = QVBoxLayout(self)
        #label
        tree_label = QLabel("label")
        #tree view
        self.tree_model = QDirModel()
        root = self.tree_model.index(sutie_path)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setRootIndex(root)

        #add 按钮
        self.add_button = QPushButton("add")
        self.add_button.clicked.connect(self.add_button_func)

        tree_layout.addWidget(tree_label)
        tree_layout.addWidget(self.tree_view)
        tree_layout.addWidget(self.add_button)

    def add_button_func(self, bool):
        index = self.tree_view.currentIndex()
        file_path = self.get_root_path(index,"")

        self._top.list_view.add_file(file_path)
        
    def get_root_path(self, index, file_name):
        name_index = index.sibling(index.row(),0)  
        name = name_index.data()

        parent = index.parent()
        if parent.isValid() is False or parent.data() == BIN_DIR_NAME.CASE:
            #是顶层
            if file_name == "":
                return name
            return os.path.join(name, file_name)
        else:
            #不是顶层
            if file_name == "":
                return self.get_root_path(parent, name)
            return self.get_root_path(parent,os.path.join(name, file_name))

class CaseView(QWidget):
    def __init__(self, *args, **kw):
        super(CaseView, self).__init__(*args, **kw)
        
        #主布局
        layout = QVBoxLayout()
        #界面分割器
        splitter = QSplitter(Qt.Horizontal)     

        #界面不能被分割为0
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(1)

        #文件路径 treeview
        self.tree_view = TreeView(self,splitter)
        #选取的文件 listview
        self.list_view = ListWidget(self,splitter)

        layout.addWidget(splitter)
        self.setLayout(layout)
        
        

