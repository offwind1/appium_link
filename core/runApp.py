
"""
@author: hyt
@time：2019-03-27
"""

from core.ExecuteCase import start_case
# print(2)
# from core.report import report

class RunApp(object):
    def __init__(self, device, cml_path):
        self.device_name = device
        self.cml_path = cml_path
        
    def case_start(self):

        s = start_case()
        s.init_xml(self.cml_path, self.device_name)