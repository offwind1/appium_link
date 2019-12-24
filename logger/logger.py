
"""
@author: hyt
@time：2019-03-27
"""

import logging
from work_box.define import *

LOGGING_TAG = "_"
TAG_LIST = [LOGGING_TAG,"."]

logger = logging.getLogger(LOGGING_TAG)
logger.setLevel(level = logging.INFO)

handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s][%(name)s](%(levelname)s): %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console_formatter = logging.Formatter('[%(asctime)s][%(name)s](%(levelname)s): %(message)s')
console.setFormatter(console_formatter)

logger.addHandler(handler)
logger.addHandler(console)


def get_logger(class_name):
    return logging.getLogger("".join(TAG_LIST+[class_name]))


def set_logger(obj):
    obj.logger = get_logger(obj.__name__)
    return obj