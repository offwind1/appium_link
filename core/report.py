
"""
@author: hyt
@time：2019-03-27
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import jinja2
import json
import threading
import re
from work_box.define import *
from work_box.shell import ADB

import time, timeit

def gr(V, value):
    return V.get_real_value(value)

def get_FileSize(filePath):
    fsize = os.path.getsize(filePath)
    fsize = fsize/float(1024*1024)
    return round(fsize,2)

class R_Action(object):
    def __init__(self, node, V, flag_data):
        self.data = {
        }
        self.data.update(flag_data)

        for key in node.attrib:
            value = node.attrib[key]
            self.data.update({
                key: str(gr(V, value))
            })

    def init(self):
        return self.data

class R_Case(object):
    def __init__(self, node, filename):
        self.action_list = []
        self.data = {
            "action_list":[]
        }

        path, file_ = os.path.split(filename)

        # self.data.update(node.attrib)
        self.data.update({
            "file_name": file_
        })

    def init(self):
        return self.data

    def add_action(self, node, V, flag):
        action = R_Action(node, V, flag)
        self.action_list.append(action)
        self.data["action_list"].append(action.init())

class R_Device(object):
    def __init__(self, partent, device_info, package):
        self.device_name = device_info.get_device_name()
        self.package = package
        self.partent = partent
        self.case_list = []
        self.data = {
            "case_list":[]
        }

        self.mem_list = []
        self.mem_p_list = []
        self.cpu_list = []
        self.flag = True
        self.t = None

        self.adb = ADB(self.device_name)

        self.data.update(device_info.get_info())
        # self.save_xinneng_data()

        self.adb.clear_log()

    def out_log(self):
        log_path = os.path.join(self.partent.report_path, "{}.log".format(self.device_name))
        self.adb.save_log(log_path)
        return log_path

    def out_xinneng(self):
        self.flag = False
        self.t.join()

        return {self.device_name:{
                "cpu_list":self.cpu_list,
                "mem_list":self.mem_list
            }
        }

    def save_xinneng_data(self):
        #记录性能函数
        self.t = threading.Thread(target=self.save_xinneng, args=())
        self.t.start()
        
    def save_xinneng(self):
        adb = ADB(self.device_name)
        package_name = self.package
        while self.flag:
            time.sleep(1)

            now_time = time.localtime()
            _time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
            # print("save_xinneng", _time)

            cpu = adb.get_cpu(package_name)
            mem = adb.get_mem(package_name)

            if cpu:
                self.cpu_list.append((_time, cpu))
            if mem:
                self.mem_list.append((_time, mem))

    def init(self):
        return self.data

    def add_start_info(self, start_info):
        self.data.update(start_info)

    def add_install_info(self, install_info):
        self.data.update(install_info)

    def add_case(self, node, filename):
        case = R_Case(node, filename)
        self.case_list.append(case)
        self.data["case_list"].append(case.init())

    def add_action(self, node, V, flag):
        if self.case_list:
            case = self.case_list[-1]
            case.add_action(node, V, flag)
        else:
            # print("none case_list", self.data, node, V, flag)
            print("-")

    def screenshot(self):
        #TODO 截图
        adb = ADB(self.device_name)
        screenshot_name = "{}_{}.png".format(self.device_name, time.time())
        screenshot_path = os.path.join(self.partent.SC_SHOT_PATH, screenshot_name)
        adb.screenshot_error(screenshot_name, screenshot_path)

        return screenshot_path
    
class Report(object):
    def __init__(self):
        print("-------Report init------")

        self.data = {
            "device_list":[]
        }
        self.dev_dic = {}

    def start_report(self):
        def decorator(func):
            def wrapper(*args, **kwargs):

                func(*args, **kwargs)
                _time = self.creat_file()
                self.data.update({"test_time":_time})
                self.load_apk_info(*args, **kwargs)
            return wrapper
        return decorator 
    
    def save_xinneng(self):
        def decorator(func):
            def wrapper(*args, **kwargs):
                obj = args[2]
                device = self.dev_dic[obj.device_name]
                device.save_xinneng_data()
                return func(*args, **kwargs)
            return wrapper
        return decorator 

    def creat_file(self):
        now_time = time.localtime()
        _time = time.strftime("%Y%m%d%H%M%S", now_time)
        self.report_path = os.path.join(REPORT_PATH, _time)
        self.SC_SHOT_PATH = os.path.join(self.report_path, "screenshot")    #报告中，截图的路径 bin/时间戳/screenshot
        os.makedirs(self.SC_SHOT_PATH) 
        return time.strftime("%Y-%m-%d %H:%M:%S", now_time)

    def add_device(self):
        def decorator(func):
            def wrapper(*args, **kwargs):
                device_info = func(*args, **kwargs)
                obj = args[0]
                package = obj.apk_info.get_app_package()

                device_name = device_info.get_device_name()
                device = R_Device(self, device_info, package)
                self.dev_dic[device_name] = device
                self.data["device_list"].append(device.init())

                return device_info
            return wrapper
        return decorator 

    def start_install_app(self):
        def decorator(func):
            def wrapper(*args, **kwargs):
                obj = args[0]
                device_name = obj.device_name
                device = self.dev_dic[device_name]

                install_info = func(*args, **kwargs)
                device.add_install_info(install_info)

                return install_info
            return wrapper
        return decorator 

    def start_start_app(self):
        def decorator(func):
            def wrapper(*args, **kwargs):
                obj = args[0]
                device_name = obj.device_name
                device = self.dev_dic[device_name]

                start_info = func(*args, **kwargs)
                device.add_start_info(start_info)

                return start_info
            return wrapper
        return decorator 
    
    def add_case(self):
        def decorator(func):
            def wrapper(*args, **kwargs):
                obj, node, filename = args
                device_name = obj.device_name
                device = self.dev_dic[device_name]
                device.add_case(node, filename)

                func(*args, **kwargs)

            return wrapper
        return decorator 

    def add_action(self):
        def decorator(func):
            def wrapper(*args, **kwargs):
                obj, node, V = args
                device_name = obj.device_name
                device = self.dev_dic[device_name]

                try:
                    func(*args, **kwargs)
                    device.add_action(node, V, {
                        "state":"True"
                    })
                except Exception as e:
                    screenshot_path = device.screenshot()
                    device.add_action(node, V, {
                        "state":"False",
                        "message":str(e),
                        "screenshot":screenshot_path
                    })
                    raise e
                # func(*args, **kwargs)

            return wrapper
        return decorator 

    def end_sutie(self):
        def decorator(func):
            def wrapper(*args, **kwargs):
                func(*args, **kwargs)
                obj =args[0]
                device_name = obj.device_name
                device = self.dev_dic[device_name]
                device.flag = False

            return wrapper
        return decorator 

    def end_test(self):
        def decorator(func):
            def wrapper(*args, **kwargs):
                func(*args, **kwargs)
                #输出 report 文件
                report_json = self.out()
                xinneng = self.get_xinneng()
                log_dic = self.creat_log_js(self.get_log())
                
                self.creat_index_html(report_json, xinneng, log_dic)

            return wrapper
        return decorator 

    def creat_log_js(self, log_dic):
        log = {}
        for dev_key in log_dic:
            dev_log_path = log_dic[dev_key]
            try:
                lis = self.read_log_file(dev_log_path)
                log.update({dev_key:lis})
            except Exception as e:
                print(e)
            
        return log
        # self.creat_log(lis, dev_key)

    def creat_log(self, log_json, device):
        """
        生成index.html
        """
        # GenPages.creat_report_dir(report_path)
        self.creat_report_dir()

        template_loader = jinja2.FileSystemLoader(searchpath=PEPORT_PRO_PATH)
        template_env = jinja2.Environment(loader=template_loader)

        _templateVars = {
            'log': log_json
        }
        
        template = template_env.get_template("11111.html")

        with open(self.report_path + '/{}.html'.format(device), 'w', encoding='utf-8') as f:
            f.write(template.render(_templateVars))
        
    def read_log_file(self, file_path):
        lis = []
        if os.path.exists(file_path):
            with open(file_path,'r',encoding='ISO-8859-1') as f:
                for line in f:
                    if line !="\n":
                        a = re.findall("(\d{2}-\d{2} +\d{2}:\d{2}:\d{2}.\d{3}) +(\d{0,5}) +(\d{0,5}) +(\w) +(.+?): +(.+)", line)
                        if a:
                            lis.append(a)
        return lis

    def creat_index_html(self, report_json, xinneng, log):
        """
        生成index.html
        """
        # GenPages.creat_report_dir(report_path)
        self.creat_report_dir()

        template_loader = jinja2.FileSystemLoader(searchpath=PEPORT_PRO_PATH)
        template_env = jinja2.Environment(loader=template_loader)

        _templateVars = {
            'json': report_json,
            'xinneng':xinneng,
            'log':log
        }
        
        template = template_env.get_template("test")

        with open(self.report_path + '/test.js', 'w', encoding='utf-8') as f:
            f.write(template.render(_templateVars))
    
    def creat_report_dir(self):
        import shutil
        CSS = os.path.join(PEPORT_PRO_PATH, "css")
        IMG = os.path.join(PEPORT_PRO_PATH, "img")
        JS = os.path.join(PEPORT_PRO_PATH, "js")
        INDEX = os.path.join(PEPORT_PRO_PATH, "index.html")

        CSS_ = os.path.join(self.report_path, "css")
        IMG_ = os.path.join(self.report_path, "img")
        JS_ = os.path.join(self.report_path, "js")
        INDEX_ = os.path.join(self.report_path, "index.html")

        if not os.path.exists(CSS_):
            shutil.copytree(CSS, CSS_)
        if not os.path.exists(IMG_):
            shutil.copytree(IMG, IMG_)
        if not os.path.exists(JS_):
            shutil.copytree(JS, JS_)
        shutil.copyfile(INDEX, INDEX_)

    def get_xinneng(self):
        xinneng_dic={}
        for key in self.dev_dic:
            device = self.dev_dic[key]
            data = device.out_xinneng()
            xinneng_dic.update(data)

        json_ = json.dumps(
                    xinneng_dic,
                    ensure_ascii=False)

        return json_

    def get_log(self):
        log_dic = {}
        for key in self.dev_dic:
            device = self.dev_dic[key]
            log_path = device.out_log()
            log_dic.update({key: log_path})

        return log_dic

    def out(self):
        data = json.dumps(
                    self.data,
                    ensure_ascii=False, 
                    sort_keys=True, 
                    indent=4, 
                    separators=(',', ':'))

        return data
    
    def load_apk_info(self, *args, **kwargs):
        #记录apk 内容
        obj = args[0]
        apk_info = obj.apk_info
        self.data.update(apk_info.get_info())



if __name__ == '__main__':
    # Report().read_log_file(r"D:\Documents\appium_link\appium-lich-master\bin\report\20190128145556\ONONDYWKLBLZ6HEY.log")

    # line = """01-29 15:47:08.874   777  2433 W ActivityManager: Unbind failed: could not find connection for android.os.BinderProxy@39acc39"""

    # # a = re.findall("(\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}) (\d{0,5}) (\d{0,5}) (\w) (.+)", line)
    # a = re.findall("(\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}) +(\d{0,5}) +(\d{0,5}) +(\w) +(.+)", line)
    # print(a)


    Report().creat_log_js({"eeeeee":r"D:\Documents\appium_link\appium-lich-master\bin\report\20190129154606\ONONDYWKLBLZ6HEY.log"})