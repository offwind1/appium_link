
"""
@author: hyt
@time：2019-03-27
"""

from .baseItem import *

class Action_Wait_Widget(BaseWidget):
    key = "wait"
    def __init__(self, item):
        super(Action_Wait_Widget, self).__init__(item)
        layout = self.layout()

        form_layout = QFormLayout()
        
        self.wait_count_edit = QLineEdit()
        self.wait_count_edit.setMaximumWidth(200)
        self.wait_count_edit.editingFinished.connect(
            lambda: self.set_title_edit(self.item.name+": "+self.wait_count_edit.text()+"s")
        )
        form_layout.addRow("等待时间(s):", self.wait_count_edit)
        layout.addLayout(form_layout)

        layout.addStretch(1)

    def self_to_data(self):
        self.data["wait"] = self.wait_count_edit.text()

    def update(self, data):
        self.wait_count_edit.setText(data["wait"])

    def self_to_xml(self, node):
        node.attrib.update(self.data)
        return node

class Action_Wait_Item(BaseItem):
    name = "等待"
    #可以拖拽，不能包容
    state = ItemState.CAN_DRAG | ItemState.CONNOT_INCLUDE
    #可以有删除复制，不能有黏贴和动作
    menu = ItemState.MENU_COPY | ItemState.MENU_DELETE

    def __init__(self,*args,**kw):
        qicon = QIcon(os.path.join(IMAGE_PATH, "wait.png"))
        super(Action_Wait_Item, self).__init__(qicon)
        self.view = Action_Wait_Widget(self)

