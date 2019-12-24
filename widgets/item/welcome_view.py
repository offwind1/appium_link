
"""
@author: hyt
@time：2019-03-27
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class WelcomeView(QFrame):
    def __init__(self):
        super(WelcomeView, self).__init__()
        # self.setMinimumWidth(100)
        self.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(self)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setFont(QFont("Roman times",15,QFont.Bold))
        self.label.setText("Welcome Use AppiumLink")

        layout.addWidget(self.label)
        self.setLayout(layout)
