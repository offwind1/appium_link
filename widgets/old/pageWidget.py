from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utility.define import *
from utility.tools import getYaml

class PageList(QWidget):
    def __init__(self, *args, **kw):
        super(PageList, self).__init__(*args, **kw)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.listview = QListWidget()
        self.listview.setMinimumWidth(300)

        layout.addWidget(self.listview)
        self.setLayout(layout)
        self.locaters = []

    def set_data(self, path):
        self.listview.clear()
        self.locaters.clear()

        data = getYaml(path)
        _, namefile = os.path.split(path)
        f, _ = os.path.splitext(namefile)

        for key in data:
            self.locaters = data[key]['locators']
            self.page = f
            
            for loc in self.locaters:
                self.listview.addItem(loc.get("name"))

    def get_page(self):
        row = self.listview.currentRow()
        if row != -1:
            data = self.locaters[row]
            data.update({"page":self.page})
            return data

        return 0

class PageWidget(QDialog):
    page_path = None

    def __init__(self, *args, **kw):
        super(PageWidget, self).__init__(*args, **kw)
        self.resize(800, 400)
        self.setWindowTitle('Input')

        layout = QVBoxLayout()

        #界面分割器
        splitter = QSplitter(Qt.Horizontal)     
        #界面不能被分割为0
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(1)

        self.__model = QFileSystemModel()
        self.__model.setRootPath(BIN_PATH)
        self.__model.setNameFilterDisables(False)
        self.__model.setNameFilters(["*.yaml"])

        
        self.treeview = QTreeView()
        self.treeview.setMinimumWidth(500)
        self.treeview.setModel(self.__model)
        self.treeview.setRootIndex(self.__model.index(BIN_PATH))
        self.treeview.clicked.connect(self.show_path)
        self.treeview.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        if PageWidget.page_path:
            i = self.__model.index(PageWidget.page_path)
            self.expanded_all(i)
        
        splitter.addWidget(self.treeview)
        
        self.listview = PageList()
        splitter.addWidget(self.listview)

        layout.addWidget(splitter)

        buttonBox = QDialogButtonBox(parent=self)
        buttonBox.setOrientation(Qt.Horizontal)  # 设置为水平方向
        buttonBox.setStandardButtons(QDialogButtonBox.Ok)  # 确定和取消两个按钮

        buttonBox.accepted.connect(self.accept)  # 确定
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    def expanded_all(self, i):
        self.treeview.setExpanded(i, True)
        if i.parent().isValid():
            self.expanded_all(i.parent())

    def accept(self):
        self.page = self.listview.get_page()
        if not self.page:
            return
        super().accept()    

    def show_path(self, event):
        index = self.treeview.currentIndex()
        path = self.__model.filePath(index)
        
        PageWidget.page_index = index

        if ".yaml" in path:
            self.listview.set_data(path)
            PageWidget.page_path = path

# def test(i):
#     print(i.row(), i.column())

#     if i.parent().isValid():
#         test(i.parent())