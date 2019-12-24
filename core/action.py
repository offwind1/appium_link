
"""
@author: hyt
@time：2019-03-27
"""
import sys,os
import re
import random
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from logger import set_logger
# from utility import L ,KeyCode
from work_box.define import *
# from utility.config import config
# from utility.exceptions import *
# from gui_tk.Define import CLICK

_package = ""

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance

def sp(func,s=1):
    def wrapper(*args, **kw):
        time.sleep(s)
        return func(*args, **kw)
    return wrapper

def log(func):
    def wrapper(*args, **kw):
        obj = args[0]
        obj.logger.info("into {}".format(func.__name__))
        f = func(*args, **kw)
        obj.logger.info("out {}".format(func.__name__))
        return f
    return wrapper

@set_logger
class ElementActions:
    def __init__(self, driver: webdriver.Remote, device = None, package=None):
        global _package 

        _package = package

        self.driver = driver
        self.width = self.driver.get_window_size()['width']
        self.height = self.driver.get_window_size()['height']
        self.device = device
        self.time = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        self.reportPath = os.path.join(SCREENSHOT_PATH,"{}/{}".format(self.device,self.time))

    def init(self, device, cml_path):
        self.device = device

    def findElementByClassName(self, name):
        return self.driver.find_elements_by_class_name(name)
    
    def reset(self):
        self.driver.reset()

    @staticmethod
    def sleep(s):
        return time.sleep(s)

    def back_press(self):
        self._send_key_event('KEYCODE_BACK')

    def dialog_ok(self, wait=5):
        locator = {'name': '对话框确认键', 'timeOutInSeconds': wait, 'type': 'id', 'value': 'android:id/button1'}
        self.click(locator)

    def set_number_by_soft_keyboard(self, nums):
        """模仿键盘输入数字,主要用在输入取餐码类似场景

        Args:
            nums: 数字
        """
        list_nums = list(nums)
        for num in list_nums:
            self._send_key_event('KEYCODE_NUM', num)

    @log
    def swip_left(self, count=1):
        """向左滑动,一般用于ViewPager

        Args:
            count: 滑动次数

        """
        for x in range(count):
            self.sleep(1)
            self.logger.info("[手势]]向左滑动 %s 次" % x)
            self.driver.swipe(self.width * 9 / 10, self.height / 2, self.width / 10, self.height / 2, 1500)

    @log
    def swip_right(self, count=1):
        """向右滑动,一般用于ViewPager

        Args:
            count: 滑动次数

        """
        for x in range(count):
            self.sleep(1)
            self.logger.info("[手势]]向左滑动 %s 次" % x)
            self.driver.swipe(self.width / 10, self.height / 2, self.width * 9 / 10, self.height / 2, 1500)

    # def click(self, locator, part=None, count=1):
    #     """基础的点击事件
    #     Args:
    #         locator:定位器
    #         count: 点击次数
    #     """
    #     el = self.getElement(locator,part)

    #     if count == 1:
    #         self.sleep(1)

    #         el.click()
    #     else:
    #         touch_action = TouchAction(self.driver)
    #         try:
    #             for x in range(count):
    #                 touch_action.tap(el).perform()
    #         except Exception as e:
    #             raise e
    @sp
    @log
    def click(self, locator, select=1, is_long_press=False, long_press_time=1):
        el = self.getElement(locator, select)

        if is_long_press:
            time = long_press_time
            self.hold(el, time)
        else:
            el.click()

    @sp
    @log
    def hold(self, element, time=1):
        """按住
        Args:
            locator:定位器
            time: 时长
        """
        x,y = self.getElementPos(element)
        self.tap_position((x,y),time)

    @log
    def getElement(self,locator,part=1):
        if part == 1 :
            return self._find_element(locator)
        return self.getOneElements(locator,part)

    @log
    def getElementPos(self, element):
        return element.center_x, element.center_y
        # return element.location['x']+element.size['width']/2,element.location['y']+element.size['height']/2

    @log
    def getOneElements(self,locator, part):
        els = self._find_elements(locator)
        leng = len(els) 

        if leng < 1:
            raise Exception("获取控件失败")
        elif leng == 1:
            return els[0]

        index = 0

        if part == 0:
            index = random.randint(1, leng)
            self.logger.info('随机获取第 {}元素'.format(index))
        elif part == -1:
            index = 0
            self.logger.info('随机获取第END元素')
        else:
            self.logger.info('获取第 {}元素'.format(part))
            if int(part) <= len(els):
                index = part
            else:
                raise NotFoundElementError
        
        return els[index-1]

    @log
    def get_text(self, locator):
        """获取元素中的text文本

        Args:
            locator:定位器
            count: 点击次数

        Returns:
            如果没有该控件返回None

        Examples:
            TextView 是否显示某内容
        """
        el = self._find_elements(locator)
        if el.__len__() == 0:
            return None
        return el[0].get_attribute("text")
    
    @log
    def get_texts(self, locator, index):
        el = self.getOneElements(locator,index)
        if el == False:
            return
        return el.get_attribute("text")

    @log
    def get_element_count(self, locator):
        els = self._find_elements(locator)
        return len(els)

    @log
    def screenshot(self, fileName):
        filePath = os.path.join(SCREENSHOT_PATH,
                            "{}\\{}\\{}&{}.png".format(
                                self.device,
                                self.time,
                                fileName.replace(':','#'),
                                time.time()))
        
        [dirname,fn]=os.path.split(filePath)
        if not os.path.exists(dirname):
            os.makedirs(dirname) 

        self.driver.save_screenshot(filePath)

    @log
    def send_key(self, locator, send, user_like):
        if user_like:
            self.text_like_user(locator, send)
        else:
            self.text(locator, send)

    @sp
    @log
    def text_like_user(self, locator, value):
        self._find_element(locator).click()

        for char in value:
            # if not ( (KeyCode.getKeyCodeBychar(char) > 100) == KeyCode.checkCapsLock() ):
            #     KeyCode.chanceCapsLock()
            #     #大小写锁定键
            #     # self.driver.keyevent(115)
            #     self.driver.press_keycode(115)
            #     print('大写键切换')
            self.driver.press_keycode( KeyCode.getKeyCodeBychar(char) - 100 
                    if KeyCode.getKeyCodeBychar(char)>100 
                    else KeyCode.getKeyCodeBychar(char) )

        self.driver.keyevent(66)
        # self.driver.hide_keyboard()66
        # self.driver.activate_ime_engine('io.appium.android.ime/.UnicodeIME')

    @sp
    @log
    def text(self, locator, value, clear_first=True, click_first=True):
        """输入文本

        Args:
            locator: 定位器
            value: 文本内容
            clear_first: 是否先清空原来文本
            click_first: 是否先点击选中
        Raises:
            NotFoundElementError

        """
        el = self._find_element(locator)
        print(el.is_displayed(), locator)
        
        if click_first:
            el.click()
        if clear_first:
            el.clear()
        el.send_keys(value)

    @sp
    @log
    def swip_free(self, startx,starty,endx,endy):
        self.driver.swipe(self.width *float(startx), self.height * float(starty), 
                        self.width *float(endx), self.height *float(endy))
        self.sleep(1)
    @sp
    @log
    def swip_down(self, count=1, method=None):
        """向下滑动,常用于下拉刷新

        Args:
            count: 滑动次数
            method: 传入的方法 method(action) ,如果返回为True,则终止刷新

        Examples:
            action.swip_down(count=100, method=lambda action: not action.is_key_text_displayed("暂无可配送的订单"))
            上面代码意思:当页面不展示"暂无可配送的订单"时停止刷新,即有单停止刷新
        """
        if count == 1:
            self.driver.swipe(self.width / 2, self.height * 2 / 5, self.width / 2, self.height * 4 / 5, 2000)
            self.sleep(1)
        else:
            for x in range(count):
                self.driver.swipe(self.width / 2, self.height * 2 / 5, self.width / 2, self.height * 4 / 5, 2000)
                self.sleep(1)
                try:
                    if method(self):
                        break
                except Exception as e:
                    raise e

    @sp
    @log
    def swip_up(self, count=1, method=None):
        """向上滑动,常用于上拉刷新

        Args:
            count: 滑动次数
            method: 传入的方法 method(action) ,如果返回为True,则终止刷新

        Examples:
            action.swip_down(count=100, method=lambda action: not action.is_key_text_displayed("暂无可配送的订单"))
            上面代码意思:当页面不展示"暂无可配送的订单"时停止刷新,即有单停止刷新
        """
        if count == 1:
            self.driver.swipe(self.width / 2, self.height * 4 / 5, self.width / 2, self.height * 2 / 5, 2000)
            self.sleep(1)
        else:
            for x in range(count):
                self.driver.swipe(self.width / 2, self.height * 4 / 5, self.width / 2, self.height * 2 / 5, 2000)
                self.sleep(1)
                try:
                    if method(self):
                        break
                except Exception as e:
                    raise e

    @log
    def is_element_text(self,locator,message):
        try:
            el = self._find_element(locator)
        except Exception as e:
            return False
        
        if el is not None:
            if message in el.text:
                return True
        
        return False

    @log
    def is_toast_show(self, message, wait=20):
        """Android检查是否有对应Toast显示,常用于断言
        Args:
            message: Toast信息
            wait:  等待时间,默认20秒
        Returns:
            True 显示Toast
        """
        locator = {'name': '[Toast] %s' % message, 'timeOutInSeconds': wait, 'type': 'xpath',
                   'value': '//*[contains(@text,\'%s\')]' % message}
        try:
            el = self._find_element(locator, is_need_displayed=False)
            return el is not None
        except NotFoundElementError:
            self.logger.error("[Toast] 页面中未能找到 %s toast" % locator)
            return False

    @log
    def is_text_displayed(self, text, is_retry=True, retry_time=5):
        """检查页面中是否有文本关键字

        如果希望检查失败的话,不再继续执行case,使用 is_raise = True

        Args:
            text: 关键字(请确保想要的检查的关键字唯一)
            is_retry: 是否重试,默认为true
            retry_time: 重试次数,默认为5
            is_raise: 是否抛异常
        Returns:
            True: 存在关键字
        Raises:
            如果is_raise = true,可能会抛NotFoundElementError

        """
        try:
            if is_retry:
                return WebDriverWait(self.driver, retry_time).until(
                    lambda driver: self._find_text_in_page(text))
            else:
                return self._find_text_in_page(text)
        except TimeoutException:
            self.logger.error("[Text]页面中未找到 %s 文本" % text)
            return False

    @log
    def is_element_displayed(self, locator, is_retry=True, ):
        """检查控件是否显示

        Args:
            is_retry:是否重试检查,重试时间为'timeOutInSeconds'
            locator: 定位器
        Returns:
            true:  显示
            false: 不显示
        """
        if is_retry:
            try:
                el = self._find_element(locator, is_need_displayed=True)
                return el is not None
            except Exception as e:
                return False
        else:
            el = self._get_element_by_type(self.driver, locator)
            return el.is_displayed()

    # ======================= private ====================

    @log
    def _find_text_in_page(self, text):
        """检查页面中是否有文本关键字
        拿到页面全部source,暴力检查text是否在source中
        Args:
            text: 检查的文本

        Returns:
            True : 存在

        """
        self.logger.info("[查找] 文本 %s " % text)
        return text in self.driver.page_source

    @log
    def _find_element(self, locator, is_need_displayed=True):
        """查找单个元素,如果有多个返回第一个

        Args:
            locator: 定位器
            is_need_displayed: 是否需要定位的元素必须展示

        Returns: 元素

        Raises: NotFoundElementError
                未找到元素会抛 NotFoundElementError 异常

        """
        if 'timeOutInSeconds' in locator:
            wait = locator['timeOutInSeconds']
        else:
            wait = 20

        try:
            if is_need_displayed:
                WebDriverWait(self.driver, wait).until(
                    lambda driver: self._get_element_by_type(driver, locator).is_displayed())
            else:
                WebDriverWait(self.driver, wait).until(
                    lambda driver: self._get_element_by_type(driver, locator) is not None)
            return self._get_element_by_type(self.driver, locator)
        except Exception as e:
            self.logger.exception("[element] 页面中未能找到 %s 元素" % locator)
            raise Exception("页面中未能找到 %s 元素" % locator)

    @log
    def _find_elements(self, locator):
        """查找多元素(不会抛异常)

        Args:
            locator: 定位器

        Returns:元素列表 或 []

        """
        if 'timeOutInSeconds' in locator:
            wait = locator['timeOutInSeconds']
        else:
            wait = 20

        try:
            WebDriverWait(self.driver, wait).until(
                lambda driver: self._get_element_by_type(driver, locator, False).__len__() > 0)
            return self._get_element_by_type(self.driver, locator, False)
        except:
            self.logger.exception("[elements] 页面中未能找到 %s 元素" % locator)
            raise Exception("页面中未能找到 %s 元素" % locator)
    
    @staticmethod
    def _get_element_by_type(driver: webdriver.Remote, locator, element=True):
        """通过locator定位元素(默认定位单个元素)

        Args:
            driver:driver
            locator:定位器
            element:
                true:查找单个元素
                false:查找多个元素

        Returns:单个元素 或 元素list

        """
        value = locator['value']
        ltype = locator['type']

        if ltype == "id":
            value_id = re.findall("(id/.+)",value)[0]
            value = str(_package)+":"+str(value_id)


        if ltype == 'name':
            ui_value = 'new UiSelector().textContains' + '(\"' + value + '\")'
            return driver.find_element_by_android_uiautomator(
                ui_value) if element else driver.find_elements_by_android_uiautomator(ui_value)
        else:
            return driver.find_element(ltype, value) if element else driver.find_elements(ltype, value)

    @log
    def _send_key_event(self, arg, num=0):
        """
        操作实体按键
        Code码：https://developer.android.com/reference/android/view/KeyEvent.html
        Args:
            arg: event_list key
            num: KEYCODE_NUM 时用到对应数字
        """
        event_list = {'KEYCODE_HOME': 3, 'KEYCODE_BACK': 4, 'KEYCODE_MENU': 82, 'KEYCODE_NUM': 8,
                        "KEYCODE_CALL":5,"KEYCODE_ENDCALL":6, "KEYCODE_SEARCH":66,"KEYCODE_POWER":26,
                        "KEYCODE_VOLUME_UP":24,"KEYCODE_VOLUME_DOWN":25}
        if arg == 'KEYCODE_NUM':
            self.driver.press_keycode(8 + int(num))
        elif arg in event_list:
            self.driver.press_keycode(int(event_list[arg]))

    @log
    def send_key_event(self, event):
        self.driver.press_keycode(int(event))

    @log
    def tap_position(self, pos, time=None):
        self.sleep(1)

        positions=[]
        positions.append(pos)
        self.driver.tap(positions, time)
    
    @log
    def tap_ratio(self,x,y,time=None):
        self.sleep(2)

        x = self.width * x
        y = self.height * y
        
        positions=[]
        positions.append((x,y))
        self.driver.tap(positions,time)

def func(z):
     try:
         z=int(z)
         return isinstance(z,int)
     except ValueError:
         return False

if __name__ == '__main__':
    pass