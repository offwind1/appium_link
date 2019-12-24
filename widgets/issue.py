
"""
@author: hyt
@time：2019-03-27
"""

from logger import set_logger
import sys

@set_logger
class Issue(object):
    onlyone = None

    OPEN_SUITE = "OPEN_SUITE"
    # CREAT_CML_FILE = "CREAT_CML_FILE"
    CHANEG_TIER = "CHANEG_TIER"
    CREAT_TAB = "CREAT_TAB"
    SELECT_ITEM_VIEW = "SELECT_ITEM_VIEW"
    SEND_ELEMENT_ID = "SEND_ELEMENT_ID"
    CHANGE_TAB_NAME = "CHANGE_TAB_NAME"
    SAVE_PROJECT = "SAVE_PROJECT"
    PALY_PROJECT = "PALY_PROJECT"
    SCREENSHOT = "SCREENSHOT"
    SEND_SWIP_POINT = "SEND_SWIP_POINT"
    CHANGE_TAB_VIEW = "CHANGE_TAB_VIEW"

    @classmethod
    def get_init(cls):
        if not cls.onlyone:
            cls.onlyone = Issue()
        return cls.onlyone

    def __init__(self):
        self.pool = {}

    def reg(self, tag, func):
        if not tag in self.pool:
            self.pool.update({
                tag:[]
            })
        rank = self.pool.get(tag,[])
        rank.append(func)

    def send(self, tag, *ars):
        rank = self.pool.get(tag,[])
        for func in rank:
            self.logger.info("call func:{} type:{} from:{} with:{}".format(func.__name__, tag, func.__self__.__class__, ars))
            try:
                func(*ars)
            except Exception:
                self.logger.exception("call func:{} type:{} from:{} with:{}".format(func.__name__, tag, func.__self__.__class__, ars))
            
