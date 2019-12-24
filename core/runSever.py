# -*- coding: utf-8 -*-

"""
@author: hyt
@time：2019-03-27
"""
import time
import subprocess
import threading
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import yaml
from appium import webdriver
from appium.webdriver.webdriver import WebDriver

from utility.environment import *
from core.runApp import RunApp
from core.ExecuteCase import start_case

# from utility import L
# from utility.shell import Shell, ADB
# from utility.tools import parse_xml
# from core.action import ElementActions


# class RunApp(object):
#     def __init__(self, device, cml_path):
#         self.device_name = device
#         self.cml_path = cml_path
        
#     def case_start(self):
#         s = start_case()

#         report.add_case(self.cml_path)
#         s.init_xml(self.cml_path, self.device_name)
#         report.out()


# class r(threading.Thread):
#     def __init__(self, device, cml_path):
#         threading.Thread.__init__(self)
#         self.device = device
#         self.cml_path = cml_path

#     def run(self):
#         runApp = RunApp(self.device, self.cml_path)
#         runApp.case_start()

def start_appium_link(device, cml_path):
    # runApp = RunApp(self.device, self.cml_path)
    # runApp.case_start()
    s = start_case()
    s.init_xml(cml_path, device)

def run_device(cml_path):
    from core.report import report

    env = Environment()
    threads = []
    tt=[]

    for device in env.devices:
        t = threading.Thread(target=start_appium_link, args=(device, cml_path,))
        threads.append(t)
    
    for t in threads:
        t.setDaemon(True)
        t.start()
        tt.append(t)

    for t in tt:
        t.join()
        
    report.out()

    print("====== test over ======")

# def run_device(cml_path):
#     env = Environment()
#     thread_list = []

#     from core.report import report

#     for device in env.devices:
#         test_run = r(device, cml_path)
#         test_run.start()
#         thread_list.append(test_run)

#     for test_run in thread_list:
#         test_run.join()
#     report.out()

if __name__ == '__main__':
    cml_path = r"D:\Documents\appium_link\appium-lich-master\bin\case\2.cml"
    run_device(cml_path)