#!/usr/bin/env python
# coding:utf-8

import os, re, time, subprocess, sys
from util.OutputText import OutputText


def write_file(filename, content, is_cover=False):
    """
    写入文件 覆盖写入
    :param filename:
    :param content:
    :param is_cover:是否覆盖写入
    :return:
    """
    try:
        newstr = ""
        if isinstance(content, list or tuple):
            for str in content:
                newstr = newstr + str + "\n"
        else:
            newstr = content
        if is_cover:
            file_mode = "w"
        else:
            file_mode = "a"
        with open(filename, file_mode) as f_w:
            f_w.writelines(newstr)
            OutputText.print_color("Write {} completed".format(filename), color=31)
    except Exception as e:
        OutputText.print_color("Write {} exception {} ".format(filename, e), color=33)


def del_files(filename):
    """
    删除文件
    :param filename:
    :return:
    """
    try:
        if os.path.exists(filename):
            subprocess.call("rm -rf {}".format(filename), shell=True)
            OutputText.print_color("Delete {} completed".format(OutputText.INDENT_2, filename), color=31)
    except Exception as e:
        OutputText.print_color("Delete {} exception {} ".format(OutputText.INDENT_2, filename, e), color=33)


def mk_dir(foldername):
    """
    创建文件目录
    :return:
    """
    try:
        if not os.path.exists(foldername):
            subprocess.call("mkdir {}".format(foldername), shell=True)
            OutputText.print_color("Create {} completed".format(OutputText.INDENT_2, foldername), color=31)
    except Exception as e:
        OutputText.print_color("Create {} exception {} ".format(OutputText.INDENT_2, foldername, e), color=33)


def read_file(filename):
    """
    读取文件
    :return:
    """
    result = ''
    try:
        with open(filename, "r") as f_r:
            result = f_r.readlines()
    except Exception as e:
        OutputText.print_color("Read {} exception {} ".format(filename, e), color=33)
    finally:
        if isinstance(result, list) and len(result) == 1:
            return result[0]
        else:
            return result
