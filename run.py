
"""
@author: hyt
@time：2019-03-27
"""

import sys
import os
import asyncio

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from quamash import QEventLoop
import multiprocessing

from logger import get_logger
from widgets import Window

logger = get_logger(__name__)

def start():
    app = QApplication(sys.argv)

    eventLoop = QEventLoop(app)
    asyncio.set_event_loop(eventLoop)

    try:
        window = Window() #Window()
        window.show()

        logger.info("window start")

        with eventLoop:
            eventLoop.run_forever()

        sys.exit(0)
    except Exception:
        logger.exception("got some error")

def start2():
    app = QApplication(sys.argv)

    window = Window()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    # start()
    multiprocessing.freeze_support()
    start2()