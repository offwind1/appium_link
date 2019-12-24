
"""
@author: hyt
@time：2019-03-27
"""

from .baseItem import *

class Logic_Execute_Widget(BaseWidget):
    key = "execute"
    PATH_MEMO = ""

    def __init__(self, item):
        super(Logic_Execute_Widget, self).__init__(item)

        layout = self.layout()

        label = QLabel("执行文件：")
        layout.addWidget(label)

        item_layout = QHBoxLayout()
        self.file_editer = QLineEdit()
        self.file_button = QPushButton("...")
        self.file_button.clicked.connect(self.open_file)

        item_layout.addWidget(self.file_editer)
        item_layout.addWidget(self.file_button)

        layout.addLayout(item_layout)
        layout.addStretch(1)

    def self_to_data(self):
        self.data["file_path"] = self.file_editer.text()

    def update(self, data):
        self.file_editer.setText(data["file_path"])

    def self_to_xml(self, node):
        node.attrib.update(self.data)
        return node

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file",Logic_Execute_Widget.PATH_MEMO,
                                                "app files (*.cml);;"
                                                "All files(*.*)")
        if filename:
            self.file_editer.setText(filename)
            
            path, file_ = os.path.split(filename)
            Logic_Execute_Widget.PATH_MEMO = path
            self.set_title_edit("执行 " + file_)

class Logic_Execute_Item(BaseItem):
    name = "执行"
    #可以拖拽，不能包容
    state = ItemState.CAN_DRAG | ItemState.CONNOT_INCLUDE
    #可以有所有菜单
    menu = ItemState.MENU_ACTION | ItemState.MENU_COPY | ItemState.MENU_DELETE | ItemState.MENU_PASTE

    def __init__(self,*args,**kw):
        qicon = QIcon(os.path.join(IMAGE_PATH, "logic.png"))
        super(Logic_Execute_Item, self).__init__(qicon)
        self.view = Logic_Execute_Widget(self)