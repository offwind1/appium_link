
"""
@author: hyt
@time：2019-03-27
"""

from .baseItem import *

class Logic_ForWidget(BaseWidget):
    key = "logic_for"

    def __init__(self, item):
        super(Logic_ForWidget, self).__init__(item)

        layout = self.layout()

        form_layout = QFormLayout()
        
        self.for_count_edit = QLineEdit()
        self.for_count_edit.setMaximumWidth(200)
        self.for_count_edit.editingFinished.connect(
            lambda: self.set_title_edit(self.item.name+":"+self.for_count_edit.text())
        )
        form_layout.addRow("循环次数:", self.for_count_edit)

        layout.addLayout(form_layout)
        layout.addStretch(1)

    def self_to_data(self):
        self.data["for_count"] = self.for_count_edit.text()

    def update(self, data):
        self.for_count_edit.setText(data["for_count"])

    def self_to_xml(self, node):
        node.attrib.update(self.data)
        return node


class Logic_ForItem(BaseItem):
    name = "For循环"
    #可以拖拽，可以包容
    state = ItemState.CAN_DRAG | ItemState.CAN_INCLUDE
    #可以有所有菜单
    menu = ItemState.MENU_ACTION | ItemState.MENU_COPY | ItemState.MENU_DELETE | ItemState.MENU_PASTE

    def __init__(self,*args,**kw):
        qicon = QIcon(os.path.join(IMAGE_PATH, "for.png"))
        super(Logic_ForItem, self).__init__(qicon)#, "循环",**kw)
        self.view = Logic_ForWidget(self)


