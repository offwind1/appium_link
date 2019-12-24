
"""
@author: hyt
@time：2019-03-27
"""

from .baseItem import *

class MainTitleWidget(BaseWidget):
    key = "main"

    def __init__(self, item):
        super(MainTitleWidget, self).__init__(item)
        layout = self.layout()

        # self.apk_info = ApkInfoView()
        # layout.addWidget(self.apk_info)

        self.value_table_view = ValueTableView2()
        layout.addWidget(self.value_table_view)

        layout.addStretch(1)

    def self_to_data(self):
        # self.apk_info.self_to_data(self.data)
        self.value_table_view.self_to_data(self.data)

    def update(self, data):
        # self.apk_info.update(data)
        self.value_table_view.update(data) 

    def self_to_xml(self, node):
        # self.apk_info.self_to_xml(node)
        self.value_table_view.self_to_xml(node, self.data)
        return node

    def xml_to_data(self, root):
        data = {}
        data.update(self.value_table_view.xml_to_data(root)) 
        # data.update(self.apk_info.xml_to_data(root))
        return data

class MainTitleItem(BaseItem):
    name = "用例进程"
    #不能拖拽，可以包容
    state = ItemState.CONNOT_DRAG | ItemState.CAN_INCLUDE
    #菜单有动作，有黏贴、没有复制和删除
    menu = ItemState.MENU_ACTION | ItemState.MENU_PASTE

    def __init__(self):
        qicon = QIcon(os.path.join(IMAGE_PATH, "action.png"))
        super(MainTitleItem, self).__init__(qicon)
        self.view = MainTitleWidget(self)

        