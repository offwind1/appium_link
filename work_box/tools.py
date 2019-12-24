# -*- coding: utf-8 -*-

"""
@author: hyt
@time：2019-03-27
"""
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import yaml
import xml.etree.cElementTree as ET
import xml.dom.minidom as minidom
from .shell import Shell

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
            # print('创建单例对象')
        return instances[class_]
    return getinstance

@singleton
class s_index:
    index = 0
    def get_index(self):
        self.index = self.index + 1
        return self.index -1


def get_FileSize(filePath):
    fsize = os.path.getsize(filePath)
    fsize = fsize/float(1024*1024)
    return round(fsize,2)

def parse_xml(path):
    """
        解析xml，返回root
    """
    if not os.path.exists(path):
        raise Exception("路径:{} 的文件不存在".format(path))

    return ET.parse(path).getroot()

def out_xml(root,out_file):
    """格式化root转换为xml文件"""
    rough_string = ET.tostring(root, encoding='utf-8')
    reared_content = minidom.parseString(rough_string)
    with open(out_file, 'w+', encoding="utf-8") as fs:
        reared_content.writexml(fs, addindent="    ", newl="\n", encoding="utf-8")
    return True

    
class Device:
    @staticmethod
    def get_android_devices():
        android_devices_list = []
        for device in Shell.invoke('adb devices').splitlines():
            if 'device' in device and 'devices' not in device:
                device = device.split('\t')[0]
                android_devices_list.append(device)
        return android_devices_list

def saveYaml(path,data):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False,allow_unicode=True)
        return True

def getYaml(path):
    if os.path.exists(path):
        with open(path,'r', encoding='UTF-8') as f:
            return yaml.load(f)
        return False
    else:
        raise NotFoundFileError

class MyEmail:
    @staticmethod
    def sendEmail(to):
        from email.mime.text import MIMEText
        from email.header import Header

        msg = MIMEText('自动化测试已结束', 'plain', 'utf-8')
        msg['From'] = MyEmail._format_addr('自动化测试工具 <%s>' % 'off_wind1@163.com')
        msg['To'] = MyEmail._format_addr('测试人员 <%s>' % to)
        msg['Subject'] = Header('测试报告', 'utf-8').encode()

        import smtplib
        server = smtplib.SMTP('smtp.163.com', 25) # SMTP协议默认端口是25
        server.set_debuglevel(1)
        server.login('off_wind1@163.com', '456852123b')
        server.sendmail('off_wind1@163.com', to, msg.as_string())
        server.quit()

    @staticmethod
    def sendEmailByContent(to,content):
        from email.mime.text import MIMEText
        from email.header import Header

        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = MyEmail._format_addr('自动化测试工具 <%s>' % 'off_wind1@163.com')
        msg['To'] = MyEmail._format_addr('测试人员 <%s>' % to)
        msg['Subject'] = Header('测试报告', 'utf-8').encode()

        import smtplib
        server = smtplib.SMTP('smtp.163.com', 25) # SMTP协议默认端口是25
        server.set_debuglevel(1)
        server.login('off_wind1@163.com', '456852123b')
        server.sendmail('off_wind1@163.com', to, msg.as_string())
        server.quit()

    @staticmethod
    def sendHtmlEmail(content:dict):
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.header import Header
        from utils.config import config

        filePath = os.path.join(config.BASE_PATH_DIR,
                                "screenshot\\{}\\{}".format(
                                    content["device"],
                                    content["time"]))

        # 邮件对象:
        msg = MIMEMultipart()
        msg['From'] = MyEmail._format_addr('自动化测试工具 <%s>' % 'off_wind1@163.com')
        msg['To'] = MyEmail._format_addr('测试人员 <%s>' % content["to"])
        msg['Subject'] = Header('测试报告', 'utf-8').encode()

        textContent = "{}\n\n\n 报告地址为：{}".format(content["content"],filePath)

        # 邮件正文是MIMEText:
        msg.attach(MIMEText(textContent, 'plain', 'utf-8'))

        # MyEmail.getPNGbyPath(filePath,msg)

        import smtplib
        server = smtplib.SMTP('smtp.163.com', 25) # SMTP协议默认端口是25
        server.set_debuglevel(1)
        server.login('off_wind1@163.com', '456852123b')
        server.sendmail('off_wind1@163.com', content["to"], msg.as_string())
        server.quit()

    @staticmethod
    def getPNGbyPath(path,msg):
        from email.mime.base import MIMEBase
        import email.encoders as encoders

        for root, dirs, files in os.walk(path):
            pass

        for filename in files:
            filePath = os.path.join(path,filename)


            with open(filePath, 'rb') as f:
                # 设置附件的MIME和文件名，这里是png类型:
                mime = MIMEBase('image', 'png', filename=filename)
                # 加上必要的头信息:
                mime.add_header('Content-Disposition', 'attachment', filename=filename)
                mime.add_header('Content-ID', '<0>')
                mime.add_header('X-Attachment-Id', '0')
                # 把附件的内容读进来:
                mime.set_payload(f.read())
                # 用Base64编码:
                encoders.encode_base64(mime)
                # 添加到MIMEMultipart:
                msg.attach(mime)

    @staticmethod
    def _format_addr(s):
        from email.utils import parseaddr, formataddr
        from email.header import Header
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

class KeyCode:
    CAPS_LOCK = False
    KEYCODE = {
            '0':7,
            '1':8,
            '2':9,
            '3':10,
            '4':11,
            '5':12,
            '6':13,
            '7':14,
            '8':15,
            '9':16,
            'A':129,
            'B':130,
            'C':131,
            'D':132,
            'E':133,
            'F':134,
            'G':135,
            'H':136,
            'I':137,
            'J':138,
            'K':139,
            'L':140,
            'M':141,
            'N':142,
            'O':143,
            'P':144,
            'Q':145,
            'R':146,
            'S':147,
            'T':148,
            'U':149,
            'V':150,
            'W':151,
            'X':152,
            'Y':153,
            'Z':154,
            'a':29,
            'b':30,
            'c':31,
            'd':32,
            'e':33,
            'f':34,
            'g':35,
            'h':36,
            'i':37,
            'j':38,
            'k':39,
            'l':40,
            'm':41,
            'n':42,
            'o':43,
            'p':44,
            'q':45,
            'r':46,
            's':47,
            't':48,
            'u':49,
            'v':50,
            'w':51,
            'x':52,
            'y':53,
            'z':54
        }

    @classmethod
    def getKeyCodeBychar(self,char):
        return self.KEYCODE[char]
    
    @classmethod
    def checkCapsLock(self):
        return self.CAPS_LOCK

    @classmethod
    def chanceCapsLock(self):
        self.CAPS_LOCK = False if self.CAPS_LOCK else True


if __name__ == '__main__':
    pass
    