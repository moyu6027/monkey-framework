#!/usr/bin/env python
# coding:utf-8

import os
from platform import uname
import subprocess
import re
from time import sleep

PATH = lambda p: os.path.abspath(os.path.join(os.path.dirname(__file__), p))

# 判断系统类型，windows使用findstr，linux使用grep
system = uname().system
if system is "Windows":
    find_util = "findstr"
else:
    find_util = "grep"

# # 判断是否设置环境变量ANDROID_HOME
# print(os.environ)
# if "ANDROID_HOME" in os.environ:
#     if computer == "Windows":
#         command = os.path.join(os.environ["ANDROID_HOME"], "platform-tools", "adb.exe")
#     else:
#         command = os.path.join(os.environ["ANDROID_HOME"], "platform-tools", "adb")
# else:
#     raise EnvironmentError(
#         "Adb not found in $ANDROID_HOME path: %s." % os.environ["ANDROID_HOME"])

'''
基本adb操作
'''


class AdbCmd():
    """
    单个设备,可不传device_id
    """

    def __init__(self, device_id=""):
        if device_id == "":
            self.device_id = ""
        else:
            self.device_id = "-s %s" % device_id

    # adb命令

    def adb(self, args):
        cmd = "%s %s %s" % ('adb', self.device_id, str(args))
        return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # adb shell命令
    def shell(self, args):
        try:
            cmd = "%s %s shell %s" % ('adb', self.device_id, str(args))
            # print(cmd)
            result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result
        except Exception as e:
            print(e)


    def attached_devices(self):
        result = self.adb("devices").stdout.read()
        devices = result.partition('\n')[2].replace('\n', '').split('\tdevice')
        return [device for device in devices if len(device) > 2]

    def hideSetting(self, packageName):
        self.shell("settings put global policy_control immersive.full=%s" % packageName)

    def push(self, local, remote):
        result = self.adb("push %s %s" % (local, remote)).stdout.read().strip()
        return result

    def push_enhance(self, local, remote):
        is_exist = False
        file = os.path.split(local)[-1]
        result = self.shell('[ -f {} ] "&&" echo "Found" "||" echo "Not"'.format(os.path.join(remote, file))).stdout.read().decode().strip()
        if result == 'Found':
            print('file is exist')
        else:
            print('file not exist')
            self.adb("push %s %s" % (local, remote)).stdout.read().strip()

    def pull(self, remote, local):
        result = self.adb("pull %s %s" % (remote, local)).stdout.read().strip()
        return result

    def getDeviceState(self):
        """
        获取设备状态： offline | bootloader | device
        """
        return self.adb("get-state").stdout.read().strip()

    def getDeviceID(self):
        """
        获取设备id号，return serialNo
        """
        return self.adb("get-serialno").stdout.read().strip()

    def getAndroidVersion(self):
        """
        获取设备中的Android版本号，如4.2.2
        """
        return self.shell("getprop ro.build.version.release").stdout.read().strip()

    def getSdkVersion(self):
        """
        获取设备SDK版本号
        """
        return self.shell("getprop ro.build.version.sdk").stdout.read().strip()

    def getDeviceModel(self):
        """
        获取设备型号
        """
        return self.shell("getprop ro.product.model").stdout.read().decode().strip()

    def getDeviceBrand(self):
        """
        获取设备厂商
        """
        return self.shell("getprop ro.product.brand").stdout.read().decode().strip()

    def getWifiStatus(self):
        """
        获取当前网络状态
        :return:
        """
        try:
            if system is "Windows":
                wifistate = self.shell("dumpsys wifi | findstr ^Wi-Fi").stdout.read().decode()
            else:
                wifistate = self.shell("dumpsys wifi | grep ^Wi-Fi").stdout.read().decode()

            if 'enabled' in wifistate:
                return 0
            else:
                return 1
        except Exception as e:
            print(e)
            return 1

    def openWifi(self):
        """
        打开wifi
        :return:
        """
        try:
            self.shell('svc wifi enable')
        except Exception as e:
            print(e)

    def checkWifi(self):
        """
        检查wifi状态,开启
        :return:
        """
        if self.getWifiStatus() == 1:
            self.openWifi()
            if self.getWifiStatus() == 0:
                print('wifi open success')
            else:
                print('wifi open fail')
        else:
            print('wifi state is open')

    def getPid(self, packageName):
        """
        获取进程pid
        args:
        - packageName -: 应用包名
        usage: getPid("com.android.settings")
        """
        if system is "Windows":
            pidinfo = self.shell("ps | findstr %s$" % packageName).stdout.read().decode()
        else:
            pidinfo = self.shell("ps | grep -w %s" % packageName).stdout.read().decode()

        if pidinfo == '':
            return "the process doesn't exist."

        pattern = re.compile(r"\d+")
        result = pidinfo.split(" ")
        result.remove(result[0])

        return pattern.findall(" ".join(result))[0]

    def killProcess(self, pid):
        """
        杀死应用进程
        args:
        - pid -: 进程pid值
        usage: killProcess(154)
        注：杀死系统应用进程需要root权限
        """
        if self.shell("kill %s" % str(pid)).stdout.read().split(": ")[-1] == "":
            return "kill success"
        else:
            return self.shell("kill %s" % str(pid)).stdout.read().split(": ")[-1]

    def kill_pid(self, keyword):
        """
        结束进程
        :param keyword:
        :return:
        """
        try:
            if system is "Windows":
                pidinfo = self.shell("ps -ef | findstr %s$" % keyword).stdout.read().decode()
            else:
                pidinfo = self.shell("ps -ef | grep -w %s" % keyword).stdout.read().decode()

            if pidinfo == '' or pidinfo is None:
                return "the process doesn't exist."
            pattern = re.compile(r"\d+")
            result = pidinfo.split(" ")
            result.remove(result[0])
            pid = pattern.findall(" ".join(result))[0]
            self.killProcess(pid)
            return 'kill {}'.format(keyword)
        except Exception as e:
            return False

    def kill_pid_re(self, keyword):
        """
        结束进程
        :param keyword:
        :return:
        """
        try:
            if system is "Windows":
                pidinfo = self.shell("ps -ef | findstr %s" % keyword).stdout.read().decode()
            else:
                pidinfo = self.shell("ps -ef | grep -w %s" % keyword).stdout.read().decode()

            if pidinfo == '' or pidinfo is None:
                return "the process doesn't exist."
            pattern = re.compile(r"\d+")
            result = pidinfo.split(" ")
            result.remove(result[0])
            pid = pattern.findall(" ".join(result))[0]
            self.killProcess(pid)
            return 'kill {}'.format(keyword)
        except Exception as e:
            return False

    def kill_pid_list(self, keyword):
        """
        结束进程
        :param keyword:
        :return:
        """
        try:
            if system is "Windows":
                pidinfo = self.shell("ps -ef | findstr %s" % keyword).stdout.read().decode()
            else:
                pidinfo = self.shell("ps -ef | grep %s | grep -v grep" % keyword).stdout.read().decode()

            if pidinfo == '' or pidinfo is None:
                return "the process doesn't exist."
            pattern = re.compile(r"\d+")
            result = pidinfo.split(" ")
            result.remove(result[0])
            pid = pattern.findall(" ".join(result))[0]
            self.killProcess(pid)
            return 'kill {}'.format(keyword)
        except Exception as e:
            return False

    def find_pid(self, keyword):
        """
        寻找进程
        :param keyword:
        :return:
        """
        is_alive = False
        try:
            if system is "Windows":
                pidinfo = self.shell("ps -ef | findstr %s$" % keyword).stdout.read().decode()
            else:
                pidinfo = self.shell("ps -ef | grep -w %s" % keyword).stdout.read().decode()

            if pidinfo == '' or pidinfo is None:
                return False
            else:
                return True
        except Exception as e:
            print(e)

    def quitApp(self, packageName):
        """
        退出app，类似于kill掉进程
        usage: quitApp("com.android.settings")
        """
        self.shell("am force-stop %s" % packageName)

    def getFocusedPackageAndWindows(self,packageName):
        """
        获取当前应用界面的windows，返回的字符串格式为：packageName/activityName[pid]
        """
        try:
            pattern = re.compile(r"[a-zA-Z0-9.]+/[a-zA-Z0-9.]+\[.*?\]")
            out = self.shell("dumpsys window %s | %s mSurface | %s name=" % (packageName, find_util, find_util)).stdout.read().decode()
            windows = pattern.findall(out)[0]
            print(windows+"#0")
            return windows+"#0"
        except Exception as e:
            print(e)

    def getFocusedPackageAndActivity(self):
        """
        获取当前应用界面的包名和Activity，返回的字符串格式为：packageName/activityName
        """
        try:
            pattern = re.compile(r"[a-zA-Z0-9.]+/[a-zA-Z0-9.]+")
            out = self.shell("dumpsys window w | %s \/ | %s name=" % (find_util, find_util)).stdout.read().decode()

            activity = pattern.findall(out)[0]
            print(activity)
            return activity
        except Exception as e:
            print(e)

    def getCurrentPackageName(self):
        """
        获取当前运行的应用的包名
        """
        return self.getFocusedPackageAndActivity().split("/")[0]

    def getCurrentActivity(self):
        """
        获取当前运行应用的activity
        """
        return self.getFocusedPackageAndActivity().split("/")[-1]

    def getBatteryLevel(self):
        """
        获取电池电量
        """
        level = self.shell("dumpsys battery | %s level" % find_util).stdout.read().split(": ")[-1]

        return int(level)

    def getBatteryStatus(self):
        """
        获取电池充电状态
        BATTERY_STATUS_UNKNOWN：未知状态
        BATTERY_STATUS_CHARGING: 充电状态
        BATTERY_STATUS_DISCHARGING: 放电状态
        BATTERY_STATUS_NOT_CHARGING：未充电
        BATTERY_STATUS_FULL: 充电已满
        """
        statusDict = {1: "BATTERY_STATUS_UNKNOWN",
                      2: "BATTERY_STATUS_CHARGING",
                      3: "BATTERY_STATUS_DISCHARGING",
                      4: "BATTERY_STATUS_NOT_CHARGING",
                      5: "BATTERY_STATUS_FULL"}
        status = self.shell("dumpsys battery | %s status" % find_util).stdout.read().split(": ")[-1]

        return statusDict[int(status)]

    def getBatteryTemp(self):
        """
        获取电池温度
        """
        temp = self.shell("dumpsys battery | %s temperature" % find_util).stdout.read().split(": ")[-1]

        return int(temp) / 10.0

    def getScreenResolution(self):
        """
        获取设备屏幕分辨率，return (width, high)
        """
        pattern = re.compile(r"\d+")
        out = self.shell("dumpsys display | %s PhysicalDisplayInfo" % find_util).stdout.read()
        display = ""
        if out:
            display = pattern.findall(out)
        elif int(self.getSdkVersion()) >= 18:
            display = self.shell("wm size").stdout.read().split(":")[-1].strip().split("x")
        else:
            raise Exception("get screen resolution failed!")
        return (int(display[0]), int(display[1]))

    def unlock_screen(self):
        """
        唤醒屏幕
        :return:
        """
        try:
            if system is "Windows":
                result = self.shell("dumpsys window policy | findstr isStatusBarKeyguard$").stdout.read().decode()
            else:
                result = self.shell("dumpsys window policy | grep isStatusBarKeyguard").stdout.read().decode()

            if "isStatusBarKeyguard=true" in result:
                print("screen start wakup!")
                self.sendKeyEvent('26')

        except Exception as e:
            return False

    def set_ime(self, input_method):
        try:
            result = self.shell("ime set {}".format(input_method))
        except Exception as e:
            return False

    def disable_ime(self, input_method):
        try:
            result = self.shell("ime disable {}".format(input_method))
        except Exception as e:
            return False

    def reboot(self):
        """
        重启设备
        """
        self.adb("reboot")

    def fastboot(self):
        """
        进入fastboot模式
        """
        self.adb("reboot bootloader")

    def getSystemAppList(self):
        """
        获取设备中安装的系统应用包名列表
        """
        sysApp = []
        for packages in self.shell("pm list packages -s").stdout.readlines():
            sysApp.append(packages.split(":")[-1].splitlines()[0])

        return sysApp

    def getThirdAppList(self):
        """
        获取设备中安装的第三方应用包名列表
        """
        thirdApp = []
        for packages in self.shell("pm list packages -3").stdout.readlines():
            thirdApp.append(packages.split(":")[-1].splitlines()[0])

        return thirdApp

    def getMatchingAppList(self, keyword):
        """
        模糊查询与keyword匹配的应用包名列表
        usage: getMatchingAppList("qq")
        """
        matApp = []
        for packages in self.shell("pm list packages %s" % keyword).stdout.readlines():
            # print(str(packages.strip().decode()))
            matApp.append(str(packages.strip().decode()).split(":")[-1].splitlines()[0])
        return matApp

    def getAppStartTotalTime(self, component):
        """
        获取启动应用所花时间
        usage: getAppStartTotalTime("com.android.settings/.Settings")
        """
        time = self.shell("am start -W %s | %s TotalTime" % (component, find_util)) \
            .stdout.read().split(": ")[-1]
        return int(time)

    def installApp(self, appFile):
        """
        安装app，app名字不能含中文字符
        args:
        - appFile -: app路径
        usage: install("d:\\apps\\Weico.apk")
        """
        self.adb("install %s" % appFile)

    def isInstall(self, packageName):
        """
        判断应用是否安装，已安装返回True，否则返回False
        usage: isInstall("com.example.apidemo")
        """
        if self.getMatchingAppList(packageName):
            return True
        else:
            return False

    def removeApp(self, packageName):
        """
        卸载应用
        args:
        - packageName -:应用包名，非apk名
        """
        self.adb("uninstall %s" % packageName)

    def clearAppData(self, packageName):
        """
        清除应用用户数据
        usage: clearAppData("com.android.contacts")
        """
        if "Success" in str(self.shell("pm clear %s" % packageName).stdout.read().splitlines()):
            return "clear user data success "
        else:
            return "make sure package exist"

    def resetCurrentApp(self):
        """
        重置当前应用
        """
        packageName = self.getCurrentPackageName()
        component = self.getFocusedPackageAndActivity()
        self.clearAppData(packageName)
        self.startActivity(component)

    def startActivity(self, component):
        """
        启动一个Activity
        usage: startActivity(component = "com.android.settinrs/.Settings")
        """
        info = self.shell("am start -W %s" % component).stdout.readlines()
        return info

    def startWebpage(self, url):
        """
        使用系统默认浏览器打开一个网页
        usage: startWebpage("http://www.baidu.com")
        """
        self.shell("am start -a android.intent.action.VIEW -d %s" % url)

    def callPhone(self, number):
        """
        启动拨号器拨打电话
        usage: callPhone(10086)
        """
        self.shell("am start -a android.intent.action.CALL -d tel:%s" % str(number))

    def sendKeyEvent(self, keycode):
        """
        发送一个按键事件
        args:
        - keycode -:
        http://developer.android.com/reference/android/view/KeyEvent.html
        usage: sendKeyEvent(keycode.HOME)
        """
        self.shell("input keyevent %s" % str(keycode))
        sleep(0.5)

    def longPressKey(self, keycode):
        """
        发送一个按键长按事件，Android 4.4以上
        usage: longPressKey(keycode.HOME)
        """
        self.shell("input keyevent --longpress %s" % str(keycode))
        sleep(0.5)

    def touch(self, e=None, x=None, y=None):
        """
        触摸事件
        usage: touch(e), touch(x=0.5,y=0.5)
        """
        if (e != None):
            x = e[0]
            y = e[1]
        if (0 < x < 1):
            x = x * self.width
        if (0 < y < 1):
            y = y * self.high

        self.shell("input tap %s %s" % (str(x), str(y)))
        sleep(0.5)

    def touchByElement(self, element):
        """
        点击元素
        usage: touchByElement(Element().findElementByName(u"计算器"))
        """
        self.shell("input tap %s %s" % (str(element[0]), str(element[1])))
        sleep(0.5)

    def touchByRatio(self, ratioWidth, ratioHigh):
        """
        通过比例发送触摸事件
        args:
        - ratioWidth -:width占比, 0<ratioWidth<1
        - ratioHigh -: high占比, 0<ratioHigh<1
        usage: touchByRatio(0.5, 0.5) 点击屏幕中心位置
        """
        self.shell("input tap %s %s" % (
            str(ratioWidth * self.getScreenResolution()[0]), str(ratioHigh * self.getScreenResolution()[1])))
        sleep(0.5)

    def swipeByCoord(self, start_x, start_y, end_x, end_y, duration=" "):
        """
        滑动事件，Android 4.4以上可选duration(ms)
        usage: swipe(800, 500, 200, 500)
        """
        self.shell(
            "input swipe %s %s %s %s %s" % (str(start_x), str(start_y), str(end_x), str(end_y), str(duration)))
        sleep(0.5)

    def swipe(self, e1=None, e2=None, start_x=None, start_y=None, end_x=None, end_y=None, duration=" "):
        """
        滑动事件，Android 4.4以上可选duration(ms)
        usage: swipe(e1, e2)
               swipe(e1, end_x=200, end_y=500)
               swipe(start_x=0.5, start_y=0.5, e2)
        """
        if (e1 != None):
            start_x = e1[0]
            start_y = e1[1]
        if (e2 != None):
            end_x = e2[0]
            end_y = e2[1]
        if (0 < start_x < 1):
            start_x = start_x * self.width
        if (0 < start_y < 1):
            start_y = start_y * self.high
        if (0 < end_x < 1):
            end_x = end_x * self.width
        if (0 < end_y < 1):
            end_y = end_y * self.high

        self.shell(
            "input swipe %s %s %s %s %s" % (str(start_x), str(start_y), str(end_x), str(end_y), str(duration)))
        sleep(0.5)

    def swipeByRatio(self, start_ratioWidth, start_ratioHigh, end_ratioWidth, end_ratioHigh, duration=" "):
        """
        通过比例发送滑动事件，Android 4.4以上可选duration(ms)
        usage: swipeByRatio(0.9, 0.5, 0.1, 0.5) 左滑
        """
        self.shell("input swipe %s %s %s %s %s" % (
            str(start_ratioWidth * self.getScreenResolution()[0]), str(start_ratioHigh * self.getScreenResolution()[1]),
            str(end_ratioWidth * self.getScreenResolution()[0]), str(end_ratioHigh * self.getScreenResolution()[1]),
            str(duration)))
        sleep(0.5)

    def swipeToLeft(self):
        """
        左滑屏幕
        """
        self.swipeByRatio(0.8, 0.5, 0.2, 0.5)

    def swipeToRight(self):
        """
        右滑屏幕
        """
        self.swipeByRatio(0.2, 0.5, 0.8, 0.5)

    def swipeToUp(self):
        """
        上滑屏幕
        """
        self.swipeByRatio(0.5, 0.8, 0.5, 0.2)

    def swipeToDown(self):
        """
        下滑屏幕
        """
        self.swipeByRatio(0.5, 0.2, 0.5, 0.8)

    def longPress(self, e=None, x=None, y=None):
        """
        长按屏幕的某个坐标位置, Android 4.4
        usage: longPress(e)
               longPress(x=0.5, y=0.5)
        """
        self.swipe(e1=e, e2=e, start_x=x, start_y=y, end_x=x, end_y=y, duration=2000)

    def longPressElement(self, e):
        """
       长按元素, Android 4.4
        """
        self.shell("input swipe %s %s %s %s %s" % (str(e[0]), str(e[1]), str(e[0]), str(e[1]), str(2000)))
        sleep(0.5)

    def longPressByRatio(self, ratioWidth, ratioHigh):
        """
        通过比例长按屏幕某个位置, Android.4.4
        usage: longPressByRatio(0.5, 0.5) 长按屏幕中心位置
        """
        self.swipeByRatio(ratioWidth, ratioHigh, ratioWidth, ratioHigh, duration=2000)





