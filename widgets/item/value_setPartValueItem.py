
"""
@author: hyt
@time：2019-03-27
"""

from .baseItem import *


class Value_setPartValueWidget(BaseWidget):
    key = "value_part"
    def __init__(self, item):
        super(Value_setPartValueWidget, self).__init__(item)
        layout = self.layout()

        self.value_table_view = ValueTableView2("value_p")
        layout.addWidget(self.value_table_view)
        
        layout.addStretch(1)

    def self_to_data(self):
        self.value_table_view.self_to_data(self.data)

    def update(self, data):
        self.value_table_view.update(data) 

    def self_to_xml(self, node):
        self.value_table_view.self_to_xml(node, self.data)
        return node

    def xml_to_data(self, root):
        return self.value_table_view.xml_to_data(root)

class Value_setPartValueItem(BaseItem):
    name = "局部变量"
    #可以拖拽，可以包容
    state = ItemState.CAN_DRAG | ItemState.CAN_INCLUDE
    #可以有所有菜单
    menu = ItemState.MENU_ACTION | ItemState.MENU_COPY | ItemState.MENU_DELETE | ItemState.MENU_PASTE

    def __init__(self,*args,**kw):
        qicon = QIcon(os.path.join(IMAGE_PATH, "value.png"))
        super(Value_setPartValueItem, self).__init__(qicon)
        self.view = Value_setPartValueWidget(self)