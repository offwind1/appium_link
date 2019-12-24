
"""
@author: hyt
@time：2019-03-27
"""
from .baseItem import *

class Action_SendKeyWidget(BaseWidget):
    key = "sendkey"

    def __init__(self, item):
        super(Action_SendKeyWidget, self).__init__(item)
        layout = self.layout()

        #选择page
        self.page_select_widget = ItemSelectWidget(self)
        layout.addWidget(self.page_select_widget)

        #输入文本表单
        form_layout = QFormLayout()

        self.send_key_edit = QLineEdit()
        self.send_key_edit.setMaximumWidth(200)
        form_layout.addRow("输入的文本:", self.send_key_edit)
        layout.addLayout(form_layout)

        #开启模拟用户输入 选择框
        self.user_send_check = QCheckBox("开启模拟用户输入", self)
        self.user_send_check.setTristate(False)
        layout.addWidget(self.user_send_check)

        layout.addStretch(1)
    
    def synchron(self, data):
        self.page_select_widget.load_from_page(data)

    def self_to_data(self):
        # page, element = self.page_select_widget.get_page()
        # self.data["page"] = page
        # self.data["element"] = element
        self.page_select_widget.self_to_data(self.data)
        self.data["send_key"] = self.send_key_edit.text()
        self.data["user_send"] = str(self.user_send_check.checkState())

    def update(self, data):
        # self.page_select_widget.load_from_page(data["page"], data["element"])
        self.page_select_widget.load_from_page(data)
        self.send_key_edit.setText(data["send_key"])
        self.user_send_check.setCheckState(int(data["user_send"]))

    def self_to_xml(self, node):
        node.attrib.update(self.data)
        return node
    

class Action_SendKeyItem(BaseItem):
    name = "发送文本"
    #可以拖拽，不能包容
    state = ItemState.CAN_DRAG | ItemState.CONNOT_INCLUDE
    #可以有删除复制，不能有黏贴和动作
    menu = ItemState.MENU_COPY | ItemState.MENU_DELETE

    def __init__(self,*args,**kw):
        qicon = QIcon(os.path.join(IMAGE_PATH, "sendkey.png"))
        super(Action_SendKeyItem, self).__init__(qicon)#, "发送文本",**kw)
        self.view = Action_SendKeyWidget(self)