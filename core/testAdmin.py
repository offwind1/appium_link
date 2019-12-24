
"""
@author: hyt
@time：2019-03-27
"""

import sys, os
import re
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from work_box.tools import *
from work_box.shell import aapt, Shell, ADB

from .project import Project
from logger import set_logger
from .report import Report
from .ExecuteCase import start_case, StartAppium
report = Report()

@set_logger
class APKInfo(object):
    def __init__(self, path):
        #从文件中，获取apk属性
        # if ".suite" in path:
        self.from_sutie_load_apk(path)
        # elif ".cml" in path:
        #     self.from_cml_load_apk(path)

    def from_sutie_load_apk(self, path):
        root = parse_xml(path)
        for apk_node in root:
            pass
        
        file_path = apk_node.attrib.get("file_path", "")
        if not os.path.exists(file_path):
            raise Exception("没有设置app")

        if file_path or file_path !="":
            self.init_data(file_path)

    def init_data(self, file_path):
        aapt_appPackage = aapt.getApkPagename(file_path)
        aapt_activity = aapt.getApkActivity(file_path)
        aapt_apklabel = aapt.getApkName(file_path)

        self.file_path = file_path
        self.apklabel = re.findall("application-label:\'(.+?)\'",aapt_apklabel)[0] if aapt_appPackage else "none"
        self.appPackage =  re.findall("name=\'(.+?)\'",aapt_appPackage)[0] if aapt_appPackage else "none"
        self.version = re.findall("versionName=\'(.+?)\'",aapt_appPackage)[0] if aapt_appPackage else "none"
        self.activity = re.findall("name=\'(.+?)\'",aapt_activity)[0] if aapt_activity else "none"
        self.file_size = get_FileSize(file_path)

        self.logger.info("""
            "应用名称"：{}
            "应用包名"：{}
            "应用版本"：{}
            "应用大小"：{}
            "应用路径"：{}
            "应用activity"：{}
        """.format(self.apklabel, self.appPackage, self.version, self.file_size, self.file_path, self.activity))

    def get_app_path(self):
        return self.file_path

    def get_app_package(self):
        return self.appPackage

    def get_app_activity(self):
        return self.activity

    def get_app_label(self):
        return self.apklabel

    def get_info(self):
        return {
            "file_path":self.file_path,
            "apklabel":self.apklabel,
            "package":self.appPackage,
            "version":self.version,
            "file_size":str(self.file_size),
            "activity":self.activity
        }

@set_logger
class Device_info(object):
    def __init__(self, device_name):
        adb = ADB(device_name)
        self.device_name = device_name
        self.device_version = adb.get_android_version()
        self.device_type = adb.get_device_type()
        self.device_sdk_version = adb.get_sdk_version()

        self.logger.info("""
            "设备名称"：{}
            "设备版本"：{}
            "设备类型"：{}
            "设备sdk版本"：{}
        """.format(
            self.device_name, 
            self.device_version, 
            self.device_type, 
            self.device_sdk_version))

    def get_info(self):
        return {
            "device_name":self.device_name,
            "device_version":self.device_version,
            "device_type":self.device_type,
            "device_sdk_version":self.device_sdk_version
        }

    def get_device_name(self):
        return self.device_name

@set_logger
class AppiumSever(StartAppium):
    @report.save_xinneng()
    def init(self, apk_info, device_info):
        self.device_name = device_info.device_name
        self.device_version = device_info.device_version

        self.file_path = apk_info.file_path
        self.package = apk_info.appPackage
        self.version = apk_info.version
        self.activity = apk_info.activity

        self.init_aport(self.device_name)
        self.start_appium()
        return self.start_driver()

    def start_driver(self):
        """
        获取driver
        """
        capabilities = {'platformName': 'Android',
                    'platformVersion': self.device_version,
                    'deviceName': self.device_name,
                    'app': self.file_path,
                    'clearSystemFiles': True,
                    'appActivity': self.activity,
                    'appPackage': self.package,
                    'automationName': 'UIAutomator2',
                    'systemPort': self.systemPort,
                    'noSign': True,
                    'unicodeKeyboard': True,
                    'resetKeyboard': True
                    }
        return self.get_driver(capabilities)
        # host = "http://localhost:"+ str(self.aport)+ "/wd/hub"
        # print(capabilities)
        # print('=============={}=========='.format(host))
        # driver = webdriver.Remote(host, capabilities)
        # return ElementActions(driver, self.device_name, self.apk_package)

@set_logger
class Sutie(start_case):
    def __init__(self, apk_info, device_info, sutie_path):
        super(Sutie, self).__init__()

        self.apk_info = apk_info
        self.device_info = device_info
        self.sutie_path = sutie_path
        self.device_name = self.device_info.get_device_name()
        self.adb = ADB(device_info.get_device_name())
        
        try:
            self.init_xml(sutie_path, self.device_name)
        except Exception as e:
            # print(e)
            self.logger.exception("Sutie")
            # raise e
        finally:
            self.end_test()

    @report.end_sutie()
    def end_test(self):
        print("{} 结束测试".format(self.device_name))
        pass

    def load_suite(self, file_xml):
        """
            读取suite文件
        """
        suite_root = parse_xml(file_xml)

        if suite_root.tag != "root":
            L.e('文件解析错误')
            sys.exit()
        
        for suite in suite_root:
            if suite.tag != "suite":
                L.e('文件解析错误 {}!= suite'.format(suite.tag))
                sys.exit()

            data = suite.attrib
            if int(data.get("update_app")):
                #安装 app
                self.step_install_app()

            #启动
            self.step_start_app()
            #启动appium
            self.start_appium(data)

            for execute in suite:
                if execute.tag != "execute":
                    continue

                file_ = execute.attrib.get("file_path")

                if ".cml" in file_:
                    try:
                        self.load_cml(file_)
                    except Exception as e:
                        # print("load_suite", e)
                        self.logger.exception("load_suite")
                        # raise e
                    finally:
                        self.action.reset()

    def start_appium(self, data):
        """开启appium,只执行一次"""
        if self.appium:
            return
        else:
            self.appium = AppiumSever()
            self.action = self.appium.init(self.apk_info, self.device_info)

    @report.add_case()
    def start_case(self, main, filename):
        super().start_case(main, filename)

    @report.add_action()
    def do_something(self, node, V):
        super().do_something(node, V)

    @report.start_start_app()
    def step_start_app(self):
        packagename = self.apk_info.get_app_package()
        activity = self.apk_info.get_app_activity()
        
        info = self.adb.get_start_app_time(packagename, activity)
        wait_time = re.findall("WaitTime: (.+)", info)
        if wait_time:
            wait_time = (float(wait_time[0]) / 1000)
            return {
                "start_state":"True",
                "start_time":wait_time
            }

        return {
            "start_state":"False",
            "start_time":wait_time
        }

    def step_install_app(self):
        #卸载
        self.adb.uninstall_apk(self.apk_info.get_app_package())

        #安装app
        install_info = self.install_app()

        if install_info.get("install_state") is None or install_info.get("install_state") == "False":
            self.logger.info("安装应用失败 log:{}".format(install_info))
            sys.exit()

    @report.start_install_app()
    def install_app(self):
        app_file = self.apk_info.get_app_path()
        app_label = self.apk_info.get_app_label()
        
        self.logger.info("{} 开始安装 {}".format(self.device_name, app_label))
        install_info = self.adb.install_app(app_file, "")
        return install_info

@set_logger
class TestAdmin(object):
    def __init__(self, file_path, project_path, apk=None):
        #case文件
        self.file_path = file_path
        self.device_list = []
        self.apk_info = apk

        Project.setProject(project_path)

        #检查环境
        self.check_appium()
        #初始化apk
        self.init_apk()
        #初始化设备
        self.init_devices()

        #开始测试
        self.start_test()
        self.end_test()

    @report.end_test()
    def end_test(self):
        print("结束测试")
        pass

    @report.start_report()
    def init_apk(self):
        "开始测试"
        if self.apk_info is None:
            self.apk_info = APKInfo(self.file_path)
    
    def init_devices(self):
        devices = self.get_devices()

        threads = []
        tt=[]

        for device_name in devices:
            t = threading.Thread(target=self.creat_device_info, args=(device_name,))
            threads.append(t)

        for t in threads:
            t.start()
            tt.append(t)

        for t in tt:
            t.join()

    def start_test(self):
        threads = []
        tt=[]

        for device_info in self.device_list:
            t = threading.Thread(target=self.start_sutie, args=(device_info,))
            threads.append(t)

        for t in threads:
            t.start()
            tt.append(t)

        for t in tt:
            t.join()

    def start_sutie(self, device_info):
        sutie = Sutie(self.apk_info, device_info, self.file_path)            

    @report.add_device()
    def creat_device_info(self, device_name):
        device_info = Device_info(device_name)
        self.device_list.append(device_info)

        return device_info

    def get_devices(self):
        devices = Device.get_android_devices()
        if not devices:
            self.logger.info('没有设备连接')
            # exit()
            sys.exit()
        else:
            self.logger.info('已连接设备:{}'.format(devices))
        return devices

    def check_appium(self):
        # L('检查appium...')
        self.logger.info('检查appium...')
        appium_v = Shell.invoke('appium -v').splitlines()[0].strip()

        # 检查appium版本
        if '1.8' not in appium_v and '1.7' not in appium_v:
            # L('appium 版本有问题')
            self.logger.info('appium 版本有问题')
            # exit()
            sys.exit()
        else:
            # L('appium version {}'.format(appium_v))
            self.logger.info('appium version {}'.format(appium_v))
    
if __name__ == '__main__':

    test_admin = TestAdmin(r"D:\Documents\appium_link\appium-lich-master\bin\case\222.suite")