
"""
@author: hyt
@time：2019-03-27
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from .issue import Issue

class ActionTabView(QTabWidget):
    def __init__(self,parent = None):
        super().__init__(parent)
        self.workTabl = parent
        self.issue = Issue.get_init()
        self.tabWidget = []

        self.setStyle()
        self.config()

    def setStyle(self):
        self.setTabsClosable(True)

    def config(self):
        self.tabCloseRequested.connect(self.closeTab)
        self.issue.reg(Issue.CREAT_TAB, self.creatTab)
        self.issue.reg(Issue.OPEN_SUITE, self.removeAllTab)
        self.issue.reg(Issue.CHANGE_TAB_NAME, self.changeTabName)
        self.currentChanged.connect(self.changeView)
    
    def changeView(self, index):
        self.issue.send(Issue.CHANGE_TAB_VIEW)

    def changeTabName(self, item, value):
        self.setTabText(self.indexOf(item.view), value)

    def removeAllTab(self, filename):
        self.clear()

    def creatTab(self, item):
        if item.view:
            f =  self.indexOf(item.view)
            if f == -1:
                index = self.addTab(item.view, item.text(0))
                self.setCurrentIndex(index)
            else:
                self.setCurrentIndex(f)

    def closeTab(self, index):
        self.removeTab(index)

