
"""
@author: hyt
@time：2019-03-27
"""

from .baseItem import *

class Value_GetValue_Widget(BaseWidget):
    key = "value_get"

    def __init__(self, item):
        super(Value_GetValue_Widget, self).__init__(item)
        layout = self.layout()

        #选择page
        self.page_select_widget = ItemSelectWidget(self)
        layout.addWidget(self.page_select_widget)

        form_layout = QFormLayout()
        
        self.save_value_edit = QLineEdit()
        self.save_value_edit.setMaximumWidth(200)
        form_layout.addRow("变量名:", self.save_value_edit)

        layout.addLayout(form_layout)

        self.select_type = QComboBox()
        self.select_type.addItem("获取控件的文本")
        self.select_type.addItem("获取控件的数量")

        layout.addWidget(self.select_type)

        form_layout2 = QFormLayout()
        self.select_edit = QLineEdit()
        self.select_edit.setMaximumWidth(200)
        form_layout2.addRow("控件组位置(0随机,-1末尾,默认1):", self.select_edit)
        layout.addLayout(form_layout2)

        layout.addStretch(1)

    def synchron(self, data):
        self.page_select_widget.load_from_page(data)

    def self_to_data(self):
        self.page_select_widget.self_to_data(self.data)
        self.data["value_name"] = self.save_value_edit.text()
        self.data["select_type"] = str(self.select_type.currentIndex())
        self.data["select"] = self.select_edit.text()

    def update(self, data):
        self.page_select_widget.load_from_page(data)
        self.save_value_edit.setText(data["value_name"])
        self.select_type.setCurrentIndex(int(data['select_type']))
        self.select_edit.setText(data["select"])

    def self_to_xml(self, node):
        node.attrib.update(self.data)
        return node


class Value_GetValue_Item(BaseItem):
    name = "提取值"
    #可以拖拽，不能包容
    state = ItemState.CAN_DRAG | ItemState.CONNOT_INCLUDE
    #可以复制删除，不能粘贴 和添加动作
    menu = ItemState.MENU_COPY | ItemState.MENU_DELETE 

    def __init__(self,*args,**kw):
        qicon = QIcon(os.path.join(IMAGE_PATH, "valueget.png"))
        super(Value_GetValue_Item, self).__init__(qicon)
        self.view = Value_GetValue_Widget(self)