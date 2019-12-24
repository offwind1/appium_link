
"""
@author: hyt
@time：2019-03-27
"""

import os

class Project(object):
    CASE_PATH = None

    @classmethod
    def setProject(cls, path):
        cls.CASE_PATH = path