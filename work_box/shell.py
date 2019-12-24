# -*- coding: utf-8 -*-

"""
@author: hyt
@time：2019-03-27
"""
import os
import sys
import platform
import re
from .define import *
# from logger import set_logger


import subprocess
# from utility.log import L
# from utility.define import *


class Shell:
    @staticmethod
    def invoke(cmd):
        # shell设为true，程序将通过shell来执行
        # stdin, stdout, stderr分别表示程序的标准输入、输出、错误句柄。
        # 他们可以是PIPE，文件描述符或文件对象，也可以设置为None，表示从父进程继承。
        # subprocess.PIPE实际上为文本流提供一个缓存区
        output, errors = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        o = output.decode("utf-8")
        return o

    def poll(cmd, pr):
        popen = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE,bufsize=1)
        while popen.poll() is None:         # None表示正在执行中
            r = popen.stdout.readline().decode("utf-8")
            # sys.stdout.write(r)                    # 可修改输出方式，比如控制台、文件等
            pr(r)
        return r
    @staticmethod
    def cmd(cmd):
        # shell设为true，程序将通过shell来执行
        # stdin, stdout, stderr分别表示程序的标准输入、输出、错误句柄。
        # 他们可以是PIPE，文件描述符或文件对象，也可以设置为None，表示从父进程继承。
        # subprocess.PIPE实际上为文本流提供一个缓存区
        return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 判断是否设置环境变量ANDROID_HOME
# if "ANDROID_HOME" in os.environ:
    # command = os.path.join(
    #     os.environ["ANDROID_HOME"],
    #     "platform-tools",
    #     "adb")

command = os.path.join(PLATFORMS_PATH, "adb")
aapt_command = os.path.join(PLATFORMS_PATH, "aapt")

# else:
#     raise EnvironmentError(
#         "Adb not found in $ANDROID_HOME path: %s." %
#         os.environ["ANDROID_HOME"])

class aapt:
    @staticmethod
    def aapt(cmd):
        print(cmd)
        output , errors = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        o = output.decode("utf-8")
        return o

    @staticmethod
    def getApkPagename(file):
        return aapt.aapt('{} dump badging "{}" | findstr package:'.format(aapt_command, file))
    
    @staticmethod
    def getApkActivity(file):
        return aapt.aapt('{} dump badging "{}" | findstr launchable-activity:'.format(aapt_command, file))

    @staticmethod
    def getApkName(file):
        return aapt.aapt('{} dump badging "{}" | findstr application-label:'.format(aapt_command, file))


class ADB(object):
    """
      参数:  device_id
    """

    def __init__(self, device_id=""):

        if device_id == "":
            self.device_id = ""
        else:
            self.device_id = "-s %s" % device_id

    def adb(self, args):
        cmd = "%s %s %s" % (command, self.device_id, str(args))
        return Shell.invoke(cmd)

    def adb_poll(self, args, pr):
        cmd = ("""%s %s %s \nexit""") % (command, self.device_id, str(args))
        
        return Shell.poll(cmd, pr)

    def shell(self, args):
        cmd = "%s %s shell %s" % (command, self.device_id, str(args),)
        return Shell.invoke(cmd)

    def __adb(self, args):
        cmd = "%s %s shell \"%s\"" % (command, self.device_id, str(args),)
        return Shell.cmd(cmd)

    def screenshot(self, file_path):
        cmd = "/system/bin/screencap -p /sdcard/screen.png"
        self.shell(cmd)
        cmd1 = "pull /sdcard/screen.png \"{}\"".format(file_path)
        self.adb(cmd1)
        return file_path

    def screenshot_error(self, screenshot_name, screenshot_path):
        """
            截图，并保存到指定的路径
            screenshot_name 图片名称
            screenshot_path 图片路径
        """
        cmd = "/system/bin/screencap -p /sdcard/{}".format(screenshot_name)
        self.shell(cmd)

        cmd1 = "pull /sdcard/{} \"{}\"".format(screenshot_name, screenshot_path)
        self.adb(cmd1)

    def get_device_state(self):
        """
        获取设备状态： offline | bootloader | device
        """
        return self.adb("get-state").stdout.read().strip()

    def get_device_id(self):
        """
        获取设备id号，return serialNo
        """
        return self.adb("get-serialno").stdout.read().strip()

    def get_android_version(self):
        """
        获取设备中的Android版本号，如4.2.2
        """
        return self.shell(
            "getprop ro.build.version.release").strip()

    def get_sdk_version(self):
        """
        获取设备SDK版本号
        """
        return self.shell("getprop ro.build.version.sdk").strip()

    def get_device_type(self):
        """
        获取设备型号
        """
        return self.shell("getprop ro.product.model").strip()

    def get_matching_app_list(self, keyword):
        """
        模糊查询与keyword匹配的应用包名列表
        usage: getMatchingAppList("qq")
        """
        packages = self.shell("pm list packages %s" % keyword)
        p = packages.split(":")#[-1].splitlines()[0]
        if len(p)>1:
            return p[-1].splitlines()[0]
        else:
            return False

    def get_size(self):
        return self.shell("wm size").strip()

    def get_uidump(self, file_name):
        self.shell("uiautomator dump /data/local/tmp/uidump.xml").strip()
        #cmd1 = "pull /sdcard/{} \"{}\"".format(file_name, path)
        self.adb("pull /data/local/tmp/uidump.xml " + file_name).strip()
        return file_name

    def get_start_app_time(self, packagename, activity):
        # "adb shell am start -w packagename/activity"
        return self.shell("am start -S -W {}/{}".format(packagename, activity)).strip()

    def uninstall_apk(self, app_page):
        self.adb("uninstall {}".format(app_page)).strip()

    def install_app(self, app_file, pr):
        """
        安装app，app名字不能含中文字符
        args:
        - appFile -: app路径
        usage: install("/Users/joko/Downloads/1.apk")
        INSTALL_FAILED_ALREADY_EXISTS	应用已经存在，或卸载了但没卸载干净	adb install 时使用 -r 参数，或者先 adb uninstall <packagename> 再安装
        INSTALL_FAILED_INVALID_APK	无效的 APK 文件
        INSTALL_FAILED_INVALID_URI	无效的 APK 文件名	确保 APK 文件名里无中文
        INSTALL_FAILED_INSUFFICIENT_STORAGE	空间不足	清理空间
        INSTALL_FAILED_DUPLICATE_PACKAGE	已经存在同名程序
        INSTALL_FAILED_NO_SHARED_USER	请求的共享用户不存在
        INSTALL_FAILED_UPDATE_INCOMPATIBLE	以前安装过同名应用，但卸载时数据没有移除	先 adb uninstall <packagename> 再安装
        INSTALL_FAILED_SHARED_USER_INCOMPATIBLE	请求的共享用户存在但签名不一致
        INSTALL_FAILED_MISSING_SHARED_LIBRARY	安装包使用了设备上不可用的共享库
        INSTALL_FAILED_REPLACE_COULDNT_DELETE	替换时无法删除
        INSTALL_FAILED_DEXOPT	dex 优化验证失败或空间不足
        INSTALL_FAILED_OLDER_SDK	设备系统版本低于应用要求
        INSTALL_FAILED_CONFLICTING_PROVIDER	设备里已经存在与应用里同名的 content provider
        INSTALL_FAILED_NEWER_SDK	设备系统版本高于应用要求
        INSTALL_FAILED_TEST_ONLY	应用是 test-only 的，但安装时没有指定 -t 参数
        INSTALL_FAILED_CPU_ABI_INCOMPATIBLE	包含不兼容设备 CPU 应用程序二进制接口的 native code
        INSTALL_FAILED_MISSING_FEATURE	应用使用了设备不可用的功能
        INSTALL_FAILED_CONTAINER_ERROR	sdcard 访问失败	确认 sdcard 可用，或者安装到内置存储
        INSTALL_FAILED_INVALID_INSTALL_LOCATION	不能安装到指定位置	切换安装位置，添加或删除 -s 参数
        INSTALL_FAILED_MEDIA_UNAVAILABLE	安装位置不可用	一般为 sdcard，确认 sdcard 可用或安装到内置存储
        INSTALL_FAILED_VERIFICATION_TIMEOUT	验证安装包超时
        INSTALL_FAILED_VERIFICATION_FAILURE	验证安装包失败
        INSTALL_FAILED_PACKAGE_CHANGED	应用与调用程序期望的不一致
        INSTALL_FAILED_UID_CHANGED	以前安装过该应用，与本次分配的 UID 不一致	清除以前安装过的残留文件
        INSTALL_FAILED_VERSION_DOWNGRADE	已经安装了该应用更高版本	使用 -d 参数
        INSTALL_FAILED_PERMISSION_MODEL_DOWNGRADE	已安装 target SDK 支持运行时权限的同名应用，要安装的版本不支持运行时权限
        INSTALL_PARSE_FAILED_NOT_APK	指定路径不是文件，或不是以 .apk 结尾
        INSTALL_PARSE_FAILED_BAD_MANIFEST	无法解析的 AndroidManifest.xml 文件
        INSTALL_PARSE_FAILED_UNEXPECTED_EXCEPTION	解析器遇到异常
        INSTALL_PARSE_FAILED_NO_CERTIFICATES	安装包没有签名
        INSTALL_PARSE_FAILED_INCONSISTENT_CERTIFICATES	已安装该应用，且签名与 APK 文件不一致	先卸载设备上的该应用，再安装
        INSTALL_PARSE_FAILED_CERTIFICATE_ENCODING	解析 APK 文件时遇到 CertificateEncodingException
        INSTALL_PARSE_FAILED_BAD_PACKAGE_NAME	manifest 文件里没有或者使用了无效的包名
        INSTALL_PARSE_FAILED_BAD_SHARED_USER_ID	manifest 文件里指定了无效的共享用户 ID
        INSTALL_PARSE_FAILED_MANIFEST_MALFORMED	解析 manifest 文件时遇到结构性错误
        INSTALL_PARSE_FAILED_MANIFEST_EMPTY	在 manifest 文件里找不到找可操作标签（instrumentation 或 application）
        INSTALL_FAILED_INTERNAL_ERROR	因系统问题安装失败
        INSTALL_FAILED_USER_RESTRICTED	用户被限制安装应用
        INSTALL_FAILED_DUPLICATE_PERMISSION	应用尝试定义一个已经存在的权限名称
        INSTALL_FAILED_NO_MATCHING_ABIS	应用包含设备的应用程序二进制接口不支持的 native code
        INSTALL_CANCELED_BY_USER	应用安装需要在设备上确认，但未操作设备或点了取消	在设备上同意安装
        INSTALL_FAILED_ACWF_INCOMPATIBLE	应用程序与设备不兼容
        does not contain AndroidManifest.xml	无效的 APK 文件
        is not a valid zip file	无效的 APK 文件
        Offline	设备未连接成功	先将设备与 adb 连接成功
        unauthorized	设备未授权允许调试
        error: device not found	没有连接成功的设备	先将设备与 adb 连接成功
        protocol failure	设备已断开连接	先将设备与 adb 连接成功
        Unknown option: -s	Android 2.2 以下不支持安装到 sdcard	不使用 -s 参数
        No space left on devicerm	空间不足	清理空间
        Permission denied ... sdcard ...	sdcard 不可用
        """
        # for line in self.adb("install -r %s" % app_file):#.stdout.readlines():
        #     # if 'Failure' in line:
        #     print(line)
        #     print(line.strip())
        import time

        time_start=time.time()
        line = self.adb("install -r %s" % app_file)
        time_end=time.time()
        t = time_end - time_start

        if 'Failure' in line:
            message = re.findall("Failure \\[(.+)\\]", line)
            return {
                "install_state":"False",
                "install_msg":message,
                "install_time":t
            }

        return {
            "install_state":"True",
            "install_time":t
        }

    def clear_log(self):
        self.shell("logcat -c").strip()
    
    def save_log(self, log_path):
        self.shell("logcat -d -v threadtime *:i >\"{}\"".format(log_path)).strip()

    def get_cpu(self, package_name):
        """
        获取当前cpu百分比
        """
        p = self.__adb(
            'top -n 1 -d 0.5 | %s %s' %
            ("grep", package_name))
        
        # while True:
        while True:
            r = p.stdout.readline().strip().decode('utf-8')
            if not r:
                return None

            if r.endswith(package_name):
                lst = [cpu for cpu in r.split(' ') if cpu]
                return int(lst[2].split('%', 1)[0])

    def __mem_pss(self, package_name):
        """
        获取当前应用内存
        """
        p = self.__adb(
            'top -n 1 -d 0.5 | %s %s' %
            ("grep", package_name))
        while True:
            r = p.stdout.readline().strip().decode('utf-8')
            if not r:
                return 0

            if r.endswith(package_name):
                lst = [mem for mem in r.split(' ') if mem]
                return int(lst[6].split('K')[0])

    def __mem_mem_total(self):
        p = self.__adb('cat proc/meminfo')
        while True:
            r = p.stdout.readline().strip().decode('utf-8')
            if not r:
                return 0

            if r and 'MemTotal' in r:
                lst = [MemTotal for MemTotal in r.split(' ') if MemTotal]
                return int(lst[1])

    def get_mem(self, package_name):
        """
        获取当前内存百分比
        """
        try:
            mem = self.__mem_pss(package_name)
            m_mem = float(self.__mem_mem_total())
            # return int(
            #     self.__mem_pss(package_name) /
            #     float(
            #         self.__mem_mem_total()) *
            #     100)

            return (int(mem/m_mem*100) , mem)
        except:
            return (0, mem)

if __name__ == "__main__":
    adb = ADB("ONONDYWKLBLZ6HEY")
    a = adb.get_mem("com.mizholdings.me2.cloudclass.debug")
    print(a)