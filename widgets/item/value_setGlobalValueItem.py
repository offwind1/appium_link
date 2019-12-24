
"""
@author: hyt
@time：2019-03-27
"""

from .baseItem import *


class Value_setGlobalValueWidget(BaseWidget):
    key = "value_global"

    def __init__(self, item):
        super(Value_setGlobalValueWidget, self).__init__(item)
        layout = self.layout()

        self.value_table_view = ValueTableView2()
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



class Value_setGlobalValueItem(BaseItem):
    name = "全局变量"
    #可以拖拽，不能包容
    state = ItemState.CAN_DRAG | ItemState.CONNOT_INCLUDE
    #可以复制删除，不能粘贴 和添加动作
    menu = ItemState.MENU_COPY | ItemState.MENU_DELETE 

    def __init__(self,*args,**kw):
        qicon = QIcon(os.path.join(IMAGE_PATH, "value_plus.png"))
        super(Value_setGlobalValueItem, self).__init__(qicon)
        self.view = Value_setGlobalValueWidget(self)