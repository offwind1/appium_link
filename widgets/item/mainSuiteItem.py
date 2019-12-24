
"""
@author: hyt
@time：2019-03-27
"""

from .baseItem import *

class MainSuiteWidget(BaseWidget):
    key = "suite"

    def __init__(self, item):
        super(MainSuiteWidget, self).__init__(item)
        layout = self.layout()

        self.apk_info = ApkInfoView()
        layout.addWidget(self.apk_info)
    
        self.update_app_check = QCheckBox("强制更新apk", self)
        self.update_app_check.setTristate(False)
        layout.addWidget(self.update_app_check)

        layout.addStretch(1)

    def self_to_data(self):
        self.apk_info.self_to_data(self.data)
        self.data["update_app"] = str(self.update_app_check.checkState())

    def update(self, data):
        self.apk_info.update(data)
        update_app = data.get("update_app")
        if update_app:
            update_app = int(update_app)
        else:
            update_app = 0
        self.update_app_check.setCheckState(update_app)

    def self_to_xml(self, node):
        self.apk_info.self_to_xml(node)
        node.attrib.update(self.data)
        return node

    def xml_to_data(self, root):
        data = {}
        data.update(self.apk_info.xml_to_data(root))
        return data

class MainSuiteItem(BaseItem):
    name = "用例集合"
    #不能拖拽，可以包容
    state = ItemState.CONNOT_DRAG | ItemState.CAN_INCLUDE
    #菜单有动作，有黏贴、没有复制和删除
    menu = ItemState.MENU_ACTION | ItemState.MENU_PASTE

    def __init__(self):
        qicon = QIcon(os.path.join(IMAGE_PATH, "action.png"))
        super(MainSuiteItem, self).__init__(qicon)
        self.view = MainSuiteWidget(self)