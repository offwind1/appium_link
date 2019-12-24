from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui_qt.apk_view import ApkView
from gui_qt.case_view import CaseView
from gui_qt.setting_view import SettingView
# from utility.define import MAIN_TAG as TAG


class WindowFactory(object):
    def onCreator(self, tag):
        if tag == TAG.ONE_VIEW_TAG:
            return ApkView()
        elif tag == TAG.TWO_VIEW_TAG:
            return CaseView()
        elif tag == TAG.THREE_VIEW_TAG:
            return SettingView()

class MainWindow(QMainWindow):    
    factory = WindowFactory()

    def __init__(self,*args,**kw):
        super(MainWindow, self).__init__(*args,**kw)
        self.setWindowTitle("My Awesome App")
        self.resize(QSize(800,500))

        pagelayout = QHBoxLayout()
        pagelayout.setContentsMargins(0,0,0,0)
        self.layout = QStackedLayout()

        pagelayout.addLayout(self.layout)
        tool_bar = QToolBar()
        tool_bar.setIconSize(QSize(32,32))

        actions = []
        for n, tag in enumerate([TAG.ONE_VIEW_TAG,TAG.TWO_VIEW_TAG,TAG.THREE_VIEW_TAG]):

            action = QAction(QIcon(os.path.join("ico","{}.png".format(tag))),tag,self)
            action.setCheckable(True)
            action.setStatusTip(tag+"界面")
            actions.append(action)
            

            action.triggered.connect(lambda c, n=n,tag=tag:self.action_triggered(c, actions, n, tag))

            w = self.factory.onCreator(tag)
            self.layout.addWidget(w)
        
        tool_bar.addActions(actions)
        widget = QWidget()
        widget.setLayout(pagelayout)

        self.addToolBar(tool_bar)
        self.setCentralWidget(widget)
        self.setStatusBar(QStatusBar())

        actions[0].setChecked(True)

    def action_triggered(self, check, actions, index, tag):
        if check == False:
            for action in actions:
                if action.text() == tag:
                    action.setChecked(True)
            return

        for action in actions:
            if action.isChecked() and action.text() != tag:
                action.setChecked(False)
        
        self.layout.setCurrentIndex(index)
