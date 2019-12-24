
"""
@author: hyt
@time：2019-03-27
"""
from .baseItem import *

class Action_Send_Key_Event_Widget(BaseWidget):
    key = "send_event"
    def __init__(self, item):
        super(Action_Send_Key_Event_Widget, self).__init__(item)
        layout = self.layout()

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        data = [('HOME键', 3), 
                ('返回键', 4), 
                ('菜单键', 82), 
                # ('KEYCODE_NUM', 8),
                # ("KEYCODE_CALL", 5),
                # ("KEYCODE_ENDCALL", 6), 
                ("搜索键", 66),
                ("电源键", 26),
                ("音量上", 24),
                ("音量下", 25)]

        for key , num in data:
            button = QRadioButton(key)
            button.toggled.connect(lambda f,n=key:self.set_title_(f,n))

            self.button_group.addButton(button)
            self.button_group.setId(button, num) 
            if num == 3:
                button.setChecked(True)
                
            layout.addWidget(button)

        layout.addStretch(1)

    def set_title_(self, flag, name):
        if flag:
            self.set_title_edit(self.item.name + ":"+name)

    def self_to_data(self):
        self.data["event"] = str(self.button_group.checkedId())

    def update(self, data):
        self.button_group.button(int(data["event"])).setChecked(True)

    def self_to_xml(self, node):
        node.attrib.update(self.data)
        return node


class Action_Send_Key_Event_Item(BaseItem):
    name = "实体键"
    #可以拖拽，不能包容
    state = ItemState.CAN_DRAG | ItemState.CONNOT_INCLUDE
    #可以有删除复制，不能有黏贴和添加动作
    menu = ItemState.MENU_COPY | ItemState.MENU_DELETE

    def __init__(self,*args,**kw):
        qicon = QIcon(os.path.join(IMAGE_PATH, "eventkey.png"))
        super(Action_Send_Key_Event_Item, self).__init__(qicon)#, "点击",**kw)
        self.view = Action_Send_Key_Event_Widget(self)

