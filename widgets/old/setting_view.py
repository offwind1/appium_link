from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
import os

from utility.config import config

class CheckBoxFactory(object):
    def onCreator(self, key, setting):
        if key == "screenshot":
            check_box = QCheckBox("报错后截屏")
        elif key == "miss":
            check_box = QCheckBox("无视报错")
        elif key == "reset":
            check_box = QCheckBox("每次执行新case重置设备")

        check_box.stateChanged.connect(lambda s,k=key:self.check_box_changed(k,s))
        state = setting.get(key)
        check_box.setCheckState(int(state))
        check_box.setContentsMargins(10,10,10,10)
        return check_box

    def check_box_changed(self, key, state):
        config.set_setting(key, str(state))

class SettingView(QWidget):

    factory = CheckBoxFactory()

    def __init__(self, *args, **kw):
        super(SettingView, self).__init__(*args, **kw)

        setting = config.get_setting()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        for key in setting:
            layout.addWidget(self.factory.onCreator(key, setting))

        self.setLayout(layout)

    
