
"""
@author: hyt
@time：2019-03-27
"""
from .baseItem import *
# from gui_qt.ui_catch_paint import *

class Action_ClickWidget(BaseWidget):
    key = "click"
    def __init__(self, item):
        super(Action_ClickWidget, self).__init__(item)
        layout = self.layout()

        #选择page
        self.page_select_widget = ItemSelectWidget(self)
        layout.addWidget(self.page_select_widget)

        #是否长按
        self.long_press_check = QCheckBox("是否长按", self)
        self.long_press_check.setTristate(False)

        layout.addWidget(self.long_press_check)

        form_layout = QFormLayout()
        
        self.long_press_edit = QLineEdit()
        self.long_press_edit.setMaximumWidth(200)
        form_layout.addRow("长按时长:", self.long_press_edit)

        self.select_edit = QLineEdit()
        self.select_edit.setMaximumWidth(200)
        form_layout.addRow("控件组位置(0随机,-1末尾,默认1):", self.select_edit)

        layout.addLayout(form_layout)

        self.label = QLabel()
        layout.addWidget(self.label)

        layout.addStretch(1)

    def synchron(self, data):
        self.page_select_widget.load_from_page(data)

    def self_to_data(self):
        self.page_select_widget.self_to_data(self.data)

        self.data["is_long_press"] = str(self.long_press_check.checkState())
        self.data["long_press_time"] = self.long_press_edit.text()
        self.data["select"] = self.select_edit.text()

    def update(self, data):
        self.page_select_widget.load_from_page(data)
        
        self.long_press_check.setCheckState(int(data["is_long_press"]))
        self.long_press_edit.setText(data["long_press_time"])
        self.select_edit.setText(data["select"])

    def self_to_xml(self, node):
        node.attrib.update(self.data)
        return node

class Action_ClickItem(BaseItem):
    name = "点击"
    #可以拖拽，不能包容
    state = ItemState.CAN_DRAG | ItemState.CONNOT_INCLUDE
    #可以有删除复制，不能有黏贴和动作
    menu = ItemState.MENU_COPY | ItemState.MENU_DELETE

    def __init__(self,*args,**kw):
        qicon = QIcon(os.path.join(IMAGE_PATH, "click.png"))
        super(Action_ClickItem, self).__init__(qicon)#, "点击",**kw)
        self.view = Action_ClickWidget(self)

