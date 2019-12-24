
"""
@author: hyt
@time：2019-03-27
"""

import sys
import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from .item.welcome_view import WelcomeView
from .issue import Issue
from logger import set_logger

@set_logger
class ShowAttribStacked(QStackedWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.issue = Issue.get_init()
        self.parent = parent

        self.setStyle()
        self.config()

    def setStyle(self):
        self.addWidget(WelcomeView())

    def config(self):
        self.issue.reg(Issue.SELECT_ITEM_VIEW, self.changeView)
        self.issue.reg(Issue.SEND_ELEMENT_ID, self.getElementId)
        self.issue.reg(Issue.SEND_SWIP_POINT, self.getSwipPoint)
        self.issue.reg(Issue.CHANGE_TAB_VIEW, self.change_tab)

    def change_tab(self, *arg):
        temp_view = self.currentWidget()
        if temp_view:
            self.removeWidget(temp_view)

    def getElementId(self, data):
        view = self.currentWidget()
        if hasattr(view, "synchron"):
            view.synchron(data)
        
    def getSwipPoint(self, data):
        view = self.currentWidget()
        if hasattr(view, "synchron_swip"):
            view.synchron_swip(data)

    def changeView(self, item):
        try:
            temp_view = self.currentWidget()
            if temp_view:
                self.removeWidget(temp_view)
            self.addWidget(item.view)
            self.setCurrentWidget(item.view)
        except Exception as e:
            self.logger.exception(e)