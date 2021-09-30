#!/usr/bin/env python3
# coding:utf-8

'''
Parser conf file to dict
'''
__author__ = 'sean.yu'

import ruamel.yaml
import os
import re
import codecs
from util.OutputText import OutputText


class ConfParser():
    def __init__(self, device_name):
        self.device_name = device_name
        self.output = OutputText()

    """
    解析配置文件,type: 'yml' or 'feature'
    """
    def parser(self, file_type='yml'):
        conf_path = os.path.join('./conf/', self.device_name + '.' + file_type)
        if not os.path.exists(conf_path):
            self.output.write_or_print('{}Conf file not exist: {}\n'.format(OutputText.INDENT_2, conf_path), color=31)
            return False
        with codecs.open(conf_path, "r", encoding='utf-8') as conf_content:
            if file_type == 'yml':
                try:
                    conf = ruamel.yaml.safe_load(conf_content)
                except ruamel.yaml.YAMLError as exc:
                    self.output.write_or_print('{}YAML Parser error: {}\n'.format(OutputText.INDENT_2, exc), color=31)
            if file_type == 'feature':
                try:
                    conf = self.givenLoad(conf_content)
                except Exception as exc:
                    self.output.write_or_print('{}Exception error: {}\n'.format(OutputText.INDENT_2, exc), color=31)

        return conf

    """
    正则文件内容获取配置内容
    """
    @staticmethod
    def givenLoad(content):
        content_str = content.read()
        ret = {}
        if (re.findall(re.compile('我希望基本导航事件中占用比例为"([^"]*)"'),content_str)) is not None:
            ret['pct_nav'] = re.findall(re.compile('我希望基本导航事件中占用比例为"([^"]*)"'),content_str)[0]
        if (re.findall(re.compile('app的package为"([^"]*)"'), content_str)) is not None:
            ret['package'] = re.findall(re.compile('app的package为"([^"]*)"'), content_str)[0]
        if (re.findall(re.compile('为我设置运行随机数值'), content_str)) is not None:
            ret['seed'] = True
        if (re.findall(re.compile('为我设置混合测试模式'), content_str)) is not None:
            ret['mix'] = True
        if (re.findall(re.compile('触摸事件在所有事件中所占的比例为"([^"]*)"'),content_str)) is not None:
            ret['pct_touch'] = re.findall(re.compile('触摸事件在所有事件中所占的比例为"([^"]*)"'),content_str)[0]

        return ret