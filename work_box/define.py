
"""
@author: hyt
@time：2019-03-27
"""
import sys
import os

#真实目录
REAL_FILE_PATH = os.path.realpath(sys.argv[0])
#BIN路径
BIN_PATH = str(os.path.abspath(os.path.join(REAL_FILE_PATH, os.pardir)))
#资源路径
RESOURCE_PATH = os.path.join(BIN_PATH, "resource")
#图片路径
IMAGE_PATH = os.path.join(RESOURCE_PATH, "icons")
#截图路径
SCREENSHOT_PATH = os.path.join(RESOURCE_PATH, "screenshot")
#LOGGER路径
LOGGER_PATH = os.path.join(BIN_PATH, "logger")
#LOG文件路径
LOG_FILE_PATH = os.path.join(LOGGER_PATH,"running_log.log")

NODE_PATH = os.path.join(BIN_PATH, "node_modules", ".bin")
APPIUM_PATH = os.path.join(NODE_PATH, "appium.cmd")

#bin文件夹下的report路径
PEPORT_PRO_PATH = os.path.join(BIN_PATH, "report")

#platforms路径
PLATFORMS_PATH = os.path.join(BIN_PATH, "platforms")

#项目路径
PROJECT_PATH = os.path.abspath(os.path.join(BIN_PATH, os.pardir))
#报告路径
REPORT_PATH = os.path.join(PROJECT_PATH, "report")
#用例路径
CASE_PATH = os.path.join(PROJECT_PATH, "case")
#apk路径
APK_PATH = os.path.join(PROJECT_PATH, "apk")


APK_INFO_VIEW_TABLE = {
    "apklabel":"应用名称",
    "package":"应用包名",
    "version":"应用版本",
    "file_path":"应用路径"
}