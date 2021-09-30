#!/usr/bin/env python
# coding:utf-8

import re
import subprocess

from util.Logging import Logging
from util.FileUtil import *


class GetAppInfo():
    def __init__(self, apkpath, device_name):
        self.device_name = device_name
        self.apkpath = apkpath
        self.logger = Logging(device_name).getlogger()
        self.appinfo = self.get_app_info()
        self.info_path = './outres/' + self.device_name + "/log/" + self.device_name + '_info.log'

    def get_app_info(self):
        """
        获取app信息
        :return:
        """
        appinfo = ''
        try:
            cmd = 'aapt dump badging {}'.format(self.apkpath)
            appinfo = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read().decode()
        except Exception as e:
            self.logger.error("获取app信息异常!{}".format(e))
        return appinfo

    def get_app_name(self):
        """
        获取app名称
        :return:
        """
        appname = ''
        try:
            if re.findall('package: name=', self.appinfo):
                appname = self.appinfo.split('package: name=')[1].split()[0].replace("'", '')
        except Exception as e:
            self.logger.error("获取app名称异常!{}".format(e))
        finally:
            write_file(self.info_path, "{}={}\n".format('package_name', appname))
            return appname

    def get_app_activity(self):
        """
        获取app的启动activity
        :return:
        """
        appactivity = ''
        try:
            if re.findall('launchable-activity: name', self.appinfo):
                appactivity = self.appinfo.split('launchable-activity: name=')[1].split()[0].replace("'", '')
        except Exception as e:
            self.logger.error("Get app launch activity exception!{}".format(e))
        finally:
            return appactivity

    def get_app_version(self):
        """
        获取app版本号
        :return:
        """
        appversion = ''
        try:
            if re.findall('package: name=', self.appinfo):
                appversion = self.appinfo.split('versionName=')[-1].replace("'", '').replace("\n", '').split()[0]
        except Exception as e:
            self.logger.error("获取app版本号异常!{}".format(e))
        finally:
            write_file(self.info_path, "{}={}\n".format('versionName', appversion))
            return appversion

    def get_android_version(self):
        """
        获取app版本号
        :return:
        """
        androidversion = ''
        try:
            if re.findall('package: name=', self.appinfo):
                androidversion = self.appinfo.split('compileSdkVersion=')[-1].replace("'", '').replace("\n", '').split()[0]
        except Exception as e:
            self.logger.error("获取android版本号异常!{}".format(e))
        finally:
            write_file(self.info_path, "{}={}\n".format('compileSdkVersion', androidversion))
            return androidversion