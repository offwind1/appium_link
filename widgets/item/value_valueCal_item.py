
"""
@author: hyt
@time：2019-03-27
"""

from .baseItem import *

class Value_ValueCal_Widget(BaseWidget):
    key = "value_cal"

    def __init__(self, item):
        super(Value_ValueCal_Widget, self).__init__(item)
        layout = self.layout()

        #输入文本表单
        form_layout = QFormLayout()

        self.key_edit = QLineEdit()
        self.key_edit.setMaximumWidth(200)
        form_layout.addRow("变量名:", self.key_edit)

        self.value_method_edit = QLineEdit()
        self.value_method_edit.setMaximumWidth(200)
        form_layout.addRow("计算式:", self.value_method_edit)

        layout.addLayout(form_layout)

        #是否长按
        self.is_global = QCheckBox("保存到全局", self)
        self.is_global.setTristate(False)

        layout.addWidget(self.is_global)

        layout.addStretch(1)

    def self_to_data(self):
        self.data["key"] = self.key_edit.text()
        self.data["method"] = self.value_method_edit.text()
        self.data["is_global"] = str(self.is_global.checkState())

    def update(self, data):
        self.key_edit.setText(data["key"])
        self.value_method_edit.setText(data["method"])
        self.is_global.setCheckState(int(data["is_global"]))

    def self_to_xml(self, node):
        node.attrib.update(self.data)
        return node

class Value_ValueCal_Item(BaseItem):
    name = "变量计算"
    #可以拖拽，不可包容
    state = ItemState.CAN_DRAG | ItemState.CONNOT_INCLUDE
    #可以复制删除，不能粘贴 和添加动作
    menu = ItemState.MENU_COPY | ItemState.MENU_DELETE 

    def __init__(self,*args,**kw):
        qicon = QIcon(os.path.join(IMAGE_PATH, "valuecal.png"))
        super(Value_ValueCal_Item, self).__init__(qicon)
        self.view = Value_ValueCal_Widget(self)