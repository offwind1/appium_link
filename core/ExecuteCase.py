
"""
@author: hyt
@time：2019-03-27
"""
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import re

from appium import webdriver
from core.action import ElementActions
# from core.report import report
from core.action import ElementActions

from .project import Project
import work_box.calculator as cal
from work_box.tools import s_index
from work_box.define import *
from work_box.shell import Shell, ADB
from work_box.tools import parse_xml, out_xml
from logger import set_logger

def is_int(z):
    """
    判断是否整数 是返回true 否返回false
    """
    try:
        z=int(z)
        return isinstance(z,int)
    except ValueError:
        return False
    
class Variable(object):
    """
    变量组，存储用例执行过程中的变量对象
    变量组拥指向父对象的指针

    根对象为全局变量，字对象为局部变量
    """

    def __init__(self, parent = None):
        self.parent = parent
        self.value_dic={}

    def add_value(self, key, value):
        """添加变量"""
        self.value_dic.update({key:value})

    def get_value(self, key):
        """
        获取变量
        若当前变量没有该值，并且变量拥有父变量
        则从父变量中查找
        """
        value = self.value_dic.get(key)
        if value is None:
            if self.parent:
                return self.parent.get_value(key)
            else:
                return ""
        else:
            return value

    def get_real_value(self, string):
        """
        获取字符串真实的值
        
        获取字符串中的变量名(用{ }括起来的)，通过变量名查找值，再依次替换字符串的内容
        """
        key_list = re.findall(r"{(.+?)}",string)

        for key in key_list:
            value = self.get_value(key)
            string = string.replace("{"+str(key)+"}", str(value))
        return string

@set_logger
class StartAppium(object):
    """
    appium启动对象
    """

    # @report.record()
    def init(self, data, device_name):
        """
        参数：
        data : cml文件的mian节点的属性，拥有app相关的参数
        device_name： 设备的名称
        """

        #设备名称
        self.device_name = device_name
        #设备版本
        self.device_version = ADB(device_name).get_android_version()

        self.init_aport(device_name)
        self.load_APKInfo(data)
        # self.start_appium()

        return self.start_driver()

    def init_aport(self, device):
        """
        初始化appium 多进程时，独立的参数
        """
        temp = device.split(':')

        if len(temp) == 1:
            self.aport = 4723 + s_index().get_index()*2
        else:
            self.aport = int(temp[1])
        
        self.bpport = self.aport + 1
        self.systemPort = 8200 + s_index().get_index()

    def load_APKInfo(self, data):
        """
        读取app参数 
        """
        self.apk_path = data.get("file_path")
        self.apk_activity = data.get("activity")
        self.apk_package = data.get("package")

        if self.apk_path is None or self.apk_path == "":
            self.logger.error('app属性未设置或文件错误')
            sys.exit()
        if self.apk_activity is None or self.apk_activity == "":
            self.logger.error('app属性未设置或文件错误')
            sys.exit()
        if self.apk_package is None or self.apk_package == "":
            self.logger.error('app属性未设置或文件错误')
            sys.exit()

    def start_appium(self):
        """
        开启appium服务器
        """
        cmd = "start cmd /k appium -p {} -bp {} -U {}".format(self.aport, self.aport + 1, self.device_name)
        # cmd = "start cmd /k {} -p {} -bp {} -U {}".format(
        #         APPIUM_PATH, 
        #         self.aport, 
        #         self.aport + 1, 
        #         self.device_name)
        print(cmd)
        Shell.cmd(cmd)

    def start_driver(self):
        """
        获取driver
        """
        capabilities = {'platformName': 'Android',
                    'platformVersion': self.device_version,
                    'deviceName': self.device_name,
                    'app': self.apk_path,
                    'clearSystemFiles': True,
                    'appActivity': self.apk_activity,
                    'appPackage': self.apk_package,
                    'automationName': 'UIAutomator2',
                    'systemPort': self.systemPort,
                    'noSign': True,
                    'unicodeKeyboard': True,
                    'resetKeyboard': True
                    }

        host = "http://localhost:"+ str(self.aport)+ "/wd/hub"
        print(capabilities)
        print('=============={}=========='.format(host))
        driver = webdriver.Remote(host, capabilities)
        return ElementActions(driver, self.device_name, self.apk_package)

    def get_driver(self, capabilities):
        host = "http://localhost:"+ str(self.aport)+ "/wd/hub"
        print(capabilities)
        print('=============={}=========='.format(host))
        driver = webdriver.Remote(host, capabilities)
        return ElementActions(driver, self.device_name, self.package)

@set_logger
class start_case(object):
    """
    运行case
    """
    def __init__(self):
        self.parse_dic = {
            "value":self.add_value,
            "click":self.click,
            "sendkey":self.send_key,
            "send_event":self.send_event,
            "swip":self.swip,
            "logic_for":self.logic_for,
            "include":self.include,
            "value_global":self.value_global,
            "value_part":self.value_part,
            "value_get":self.value_get,
            "value_p":self.add_part_value,
            "value_cal":self.value_cal,
            "wait":self.wait
        }

        self.appium = None

    def init_xml(self, file_xml, device_name):
        #设备名称
        self.device_name = device_name

        if ".cml" in file_xml:
            self.load_cml(file_xml)
        elif ".suite" in file_xml:
            self.load_suite(file_xml)

    def load_suite(self, file_xml):
        """
            读取suite文件
        """
        suite_root = parse_xml(file_xml)

        if suite_root.tag != "root":
            self.logger.error('文件解析错误')
            sys.exit()
        
        for suite in suite_root:
            if suite.tag != "suite":
                self.logger.error('文件解析错误 {}!= suite'.format(suite.tag))
                sys.exit()

            data = suite.attrib
            self.start_appium(data)

            for execute in suite:
                if execute.tag != "execute":
                    continue

                file_ = execute.attrib.get("file_path")

                if ".cml" in file_:
                    try:
                        self.load_cml(file_)
                    except Exception as e:
                        self.logger.exception("load_suite")
                        raise e
                        
                    self.action.reset()

    def load_cml(self, file_xml):
        """ 
            读取cml文件
        """
        if not os.path.exists(file_xml):
            file_xml = os.path.join(Project.CASE_PATH, file_xml)
        root = parse_xml(file_xml)

        if root.tag != "root":
            self.logger.error('文件解析错误')
            sys.exit()

        for main in root:
            if main.tag == "main":
                data = main.attrib
                self.start_appium(data)
                self.GV = Variable()
                self.start_case(main, file_xml)

    def start_appium(self, data):
        """开启appium,只执行一次"""
        if self.appium:
            return
        else:
            self.appium = StartAppium()
            self.action = self.appium.init(data, self.device_name)

    # @report.add_case()
    def start_case(self, main, filename):
        self.walk(main, self.GV)

    def walk(self, node, V):
        for action in node:
            if self.check_online(action):#若动作没有被禁用，则继续执行
                self.do_something(action, V)

    def check_online(self, node):
        """
            判断node，是否在线（启用状态）
        """
        online = node.attrib.get("online")
        if isinstance(online , str):
            flag = True
            if online.lower() == "false":
                flag = False
            return flag

        if isinstance(online ,bool):
            return online

        if online is None:
            return True

    # @report.step()
    def do_something(self, node, V):
        func = self.parse_dic.get(node.tag)
        if func:
            func(node, V)
            
    def add_value(self, node, V):
        
        #增加全局变量，
        key = node.attrib.get("name")
        value = node.attrib.get("value")
        #node.text

        #参数V不一定是全局变量，直接使用self.GV。参数传V是为了保证函数一致性
        self.GV.add_value(key, value)

    def add_part_value(self, node, V):
        
        #增加局部变量，
        key = node.attrib.get("name")
        value = node.attrib.get("value")

        #参数V不一定是全局变量，直接使用self.GV。参数传V是为了保证函数一致性
        V.add_value(key, value)
        
    def wait(self, node, V):
        pass
        time = node.attrib.get("wait")
        time = V.get_real_value(time)

        if time.isdigit():
            self.action.sleep(int(time))
        else:
            raise Exception("等待时间 不是数字 {}".format(time))

    def click(self, node, V):
        #点击操作

        temp = node.attrib
        #获取 控件id
        locator = {}
        locator['value'] = temp.get('value')
        locator['type'] = temp.get('type')
        #获取 是否长按
        long_press_time = 1 #默认长按1秒
        if temp.get('is_long_press') == "2":
            is_long_press = True
            time = temp.get('long_press_time')
            time = V.get_real_value(time)
            if is_int(time):
                long_press_time = abs(int(time))
        else:
            is_long_press = False
        #获取控件位置
        select = 1
        select_temp = temp.get('select')
        select_temp = V.get_real_value(select_temp)
        if is_int(select_temp):
            select = abs(int(select_temp))

        self.action.click(locator, select, is_long_press, long_press_time)
    
    def include(self, node, V):
        file_path = node.attrib.get("file_path")
        file_path = V.get_real_value(file_path)

        if not os.path.exists(file_path):
            file_path = os.path.join(Project.CASE_PATH, file_path)

        if os.path.exists(file_path):
            root = parse_xml(file_path)

            if root.tag != "root":
                raise Exception("读取文件错误 没有root节点")

            for main in root:
                if main.tag != "main":
                    raise Exception("文件解析错误 没有main节点")

                for action in main:
                    if action.tag != "value":
                        node.append(action)
                        self.do_something(action, V)
        else:
            self.logger.error("{} 文件不存在".format())
    
    def send_key(self, node, V):
        #发送文本

        data = node.attrib
        locator = {}
        locator['value'] = data.get('value')
        locator['type'] = data.get('type')

        send_key = data.get('send_key')
        send_key = V.get_real_value(send_key)

        if data.get('user_send') == "2":
            user_like = True
        else:
            user_like = False

        self.action.send_key(locator, send_key, user_like)

    def send_event(self, node, V):
        #发送实体键
        data = node.attrib
        event = data.get("event")
        self.action.send_key_event(event)

    def swip(self, node, V):
        data = node.attrib
        type = data.get("swip_type")

        if type == '1':     #上滑
            self.action.swip_up()
        elif type == '2':   #下滑
            self.action.swip_down()
        elif type == '3':   #左滑
            self.action.swip_left()
        elif type == '4':   #右滑
            self.action.swip_right()
        elif type == '5':
            sx = data.get("sx")
            sy = data.get("sy")
            ex = data.get("ex")
            ey = data.get("ey")

            self.action.swip_free(sx, sy, ex, ey)
            
    def logic_for(self, node, V):
        #for 循环
        
        #默认循环为1
        turn = 1

        #获取循环数
        num = node.attrib.get("for_count")
        num = V.get_real_value(num)

        if is_int(num):
            #若输入正确，替换为新的循环
            turn = abs(int(num))

        #执行循环
        for i in range(turn):
            self.walk(node, V)

    def value_global(self, node, V):
        #全局变量
        self.walk(node, V)

    def value_part(self, node, V):
        #局部变量
        PV = Variable(V)
        self.walk(node, PV)

    def value_get(self, node, V):
        data = node.attrib
        locator = {}
        locator['value'] = data.get('value')
        locator['type'] = data.get('type')

        key = data.get("value_name")
        if key is None or key == "":
            raise Exception("变量名为空")                   
        
        select = 1
        select_temp = data.get('select')
        select_temp = V.get_real_value(select_temp)
        if is_int(select_temp):
            select = abs(int(select_temp))

        select_type = data.get("select_type")

        if select_type =="0":
            value = self.action.get_texts(locator, select)
        elif select_type == "1":
            value = self.action.get_element_count(locator)

        V.add_value(key, value)

    def value_cal(self, node, V):
        data = node.attrib

        key = data.get("key")
        method = data.get("method")

        method = V.get_real_value(method)
        value = cal.calJudge(method)

        is_global = data.get("is_global")
        if is_global == "2":
            self.GV.add_value(key, value)
        else:
            V.add_value(key, value)

