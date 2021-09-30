#!/usr/bin/env python
# coding:utf-8

import re
import subprocess

from util.Logging import Logging
from util.FileUtil import *
from util.AdbCmd import AdbCmd


class AppInfo():
    def __init__(self, packageName, device_name, device_id):
        self.device_name = device_name
        self.packageName = packageName
        self.device_id = device_id
        self.adbCmd = AdbCmd(self.device_id)
        self.logger = Logging(device_name).getlogger()
        self.appinfo = self.get_app_info()
        self.info_path = './outres/' + self.device_name + "/log/" + self.device_name + '_info.log'
        write_file(self.info_path, "{}={}\n".format('package_name', self.packageName))

    def get_app_info(self):
        """
        获取app信息
        :return:
        """
        appinfo = ''
        try:
            appinfo = self.adbCmd.shell('dumpsys package {}'.format(self.packageName)).stdout.read().decode()
        except Exception as e:
            self.logger.error("获取app信息异常!{}".format(e))
        return appinfo

    def get_app_version(self):
        """
        获取app版本号
        :return:
        """
        appversion = ''
        try:
            if re.findall('versionName=', self.appinfo):
                appversion = self.appinfo.split('versionName=')[-1].replace("'", '').replace("\n", '').split()[0]
        except Exception as e:
            self.logger.error("获取app版本号异常!{}".format(e))
        finally:
            write_file(self.info_path, "{}={}\n".format('versionName', appversion))
            # return appversion

    def get_android_version(self):
        """
        获取app版本号
        :return:
        """
        androidversion = ''
        try:
            if re.findall('versionCode=', self.appinfo):
                androidversion = self.appinfo.split('targetSdk=')[-1].replace("'", '').replace("\n", '').split()[0]
        except Exception as e:
            self.logger.error("获取android版本号异常!{}".format(e))
        finally:
            write_file(self.info_path, "{}={}\n".format('compileSdkVersion', androidversion))
            # return androidversion

    def get_device_info(self):
        device_brand = ''
        device_model = ''
        try:
            device_brand = self.adbCmd.getDeviceBrand()
            device_model = self.adbCmd.getDeviceModel()
        except Exception as e:
            self.logger.error("获取设备信息异常!{}".format(e))
        finally:
            write_file(self.info_path, "{}={}\n".format('deviceInfo', (device_brand+"-"+device_model)))