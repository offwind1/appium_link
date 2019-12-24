
"""
@author: hyt
@time：2019-03-27
"""

from .baseItem import *
from .swip_paint import *

class Action_Swip_Widget(BaseWidget):
    key = "swip"
    def __init__(self, item):
        super(Action_Swip_Widget, self).__init__(item)
        layout = self.layout()
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        self.sx = 0
        self.sy = 0
        self.ex = 0
        self.ey = 0

        data = [('上滑', 1), 
                ('下滑', 2), 
                ('左滑', 3), 
                ("右滑", 4),
                ("其他", 5)]

        for name , key in data:
            button = QRadioButton(name)
            button.toggled.connect(lambda f,n=name:self.set_title_(f,n))

            self.button_group.addButton(button)
            self.button_group.setId(button, key)
            if key == 1:
                button.setChecked(True)
            layout.addWidget(button)

        # self.button = QPushButton("show", self)
        # self.button.setFixedSize(150,30)
        # self.button.clicked.connect(self.show_dialog)

        # layout.addWidget(self.button)

        self.label = QLabel()
        layout.addWidget(self.label)

        layout.addStretch(1)

    def set_title_(self, flag, name):
        if flag:
            self.set_title_edit(self.item.name + ":"+name)

    def synchron_swip(self, point):
        self.sx, self.sy ,self.ex, self.ey = point
        self.label.setText("start({},{}) end({},{})".format(self.sx,self.sy,self.ex,self.ey))

    def show_dialog(self):
        dialog = SwipPaintDialog()
        if dialog.exec_():
            start, end = dialog.point

            self.sx = start.x()
            self.sy = start.y()
            self.ex = end.x()
            self.ey = end.y()

            self.label.setText("start({},{}) end({},{})".format(self.sx,self.sy,self.ex,self.ey))

    def self_to_data(self):
        self.data["swip_type"] = str(self.button_group.checkedId())
        self.data["sx"] = str(self.sx)
        self.data["sy"] = str(self.sy)
        self.data["ex"] = str(self.ex)
        self.data["ey"] = str(self.ey)

    def update(self, data):
        self.button_group.button(int(data["swip_type"])).setChecked(True)

        self.sx = int(data["sx"])
        self.sy = int(data["sy"])
        self.ex = int(data["ex"])
        self.ey = int(data["ey"])
        self.label.setText("start({},{}) end({},{})".format(self.sx,self.sy,self.ex,self.ey))

    def self_to_xml(self, node):
        node.attrib.update(self.data)
        return node

class Action_Swip_Item(BaseItem):
    name = "滑动"
    #可以拖拽，不能包容
    state = ItemState.CAN_DRAG | ItemState.CONNOT_INCLUDE
    #可以有删除复制，不能有黏贴和动作
    menu = ItemState.MENU_COPY | ItemState.MENU_DELETE

    def __init__(self,*args,**kw):
        qicon = QIcon(os.path.join(IMAGE_PATH, "swip.png"))
        super(Action_Swip_Item, self).__init__(qicon)#, "点击",**kw)
        self.view = Action_Swip_Widget(self)

