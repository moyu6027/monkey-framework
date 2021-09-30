#!/usr/bin/env python3
# coding:utf-8
"""
Usage:
  super_ape [options] target <targets> ...

Options:
  -h --help             Show this screen
  -v --version          Show this script version

  target                Which device(s) or Group(s) you want to process

  Notice:       HCC monkey test tool.
  For Windows:  Always use double quotes for quote something;
                It's highly recommend that with get or put in Windows, always use '/' instead of '\\'
"""

"""
by sean 20190909
update at 20191217
"""
import yaml
import threading
from docopt import docopt
from monkeyutil.MonkeyRun import Run
from util.FileUtil import *
from util.GoKu import *
# from monkeyutil.Monitor import monitorRun

event = threading.Event()
INDENT_1 = 0 * ' '


def get_keys(keys, dic=None, ret=None):
    """
    从长度和结构未知的字典对象中取出指定key的值(若key的值为字典，则递归展示其最小粒度的键值对)
    keys: 可迭代容器,元素为要获取值的键
    dic: 字典对象
    ret: 一个外部的空集合, 用来存储得到的 k v 信息
    """
    for key in keys:
        if key in dic:
            if isinstance(dic[key], dict):
                get_keys(dic[key].keys(), dic=dic[key], ret=ret)
            else:
                ret.add((key, dic[key]))
        else:
            for inner in dic:
                if isinstance(dic[inner], dict):
                    get_keys([key], dic=dic[inner], ret=ret)


def get_host_info(targets):
    """从配置run_manager文件中,取得要处理的device(s)/group(s)的名称
    targets: 待处理目标(list类型),值为 all(代表所有) 或 device(s)/group(s)"""
    try:
        with open(os.path.join("conf", "run_manager.yml")) as conf_content:
            conf = yaml.load(conf_content, Loader=yaml.FullLoader)
    except Exception as e:
        OutputText.print_color("Can't parse config file: {}".format(e), color=31)
        exit(10)
    info = set()
    get_keys(targets, dic=conf, ret=info)
    return info


@timer
def main():
    global arguments
    arguments = docopt(__doc__, version="V1.0beta for HCC monkey test")
    threads = []
    for device_name, info in get_host_info(arguments['<targets>']):
        '''循环处理手机设备测试'''
        if event.is_set():
            break
        # device_id = ConfParser(device_name).parser('yml').get('device')
        # adbCmd = AdbCmd(device_id)
        # adbCmd.kill_pid('com.android.commands.monkey')
        # create log dir
        os.makedirs('./outres/' + device_name + '/log/', exist_ok=True)
        # time.sleep(1)
        monkey_run = Run(device_name)
        c = monkey_run.create_connection()
        if c == 'continue':
            continue
        elif not c:
            break
        '''放入线程'''
        t = threading.Thread(target=monkey_run.run_command)
        threads.append(t)
    for th in threads:
        # th.setDaemon(True)
        th.start()
    for th in threads:
        th.join()


if __name__ == "__main__":
    try:
        # logcatPathList = [
        #     "D:\python-scripts\monkey\outres\phone3\log\phone3_crash_logcat_20200115103802.log",
        #     "D:\python-scripts\monkey\outres\phone3\log\phone3_all_exception_logcat_20200115103802.log",
        #     "D:\python-scripts\monkey\outres\phone3\log\phone3_GC_logcat_20200115103802.log",
        #     "D:\python-scripts\monkey\outres\phone3\log\phone3_watchdog_logcat_20200115103802.log"
        # ]
        # pathdict = {
        #             'templatePath': os.path.abspath('./monkeyutil/monitor_HTML'),
        #             'monitorDataPath': os.path.abspath('./outres/phone3/monkey-monitor'),
        #             'logcatPath': logcatPathList,
        #             'deviceLogPath': 'D:\python-scripts\monkey\outres\phone3\log\phone3.log'
        # }
        # monitorRun(pathdict)
        # exit(0)
        os.makedirs('./log/', exist_ok=True)
        # print('\n'.join([''.join([('SuperApe'[(x-y) % len('SuperApe')] if ((x*0.05)**2+(y*0.1)**2-1)**3-(x*0.05)**2*(y*0.1)**3 <= 0else' ') for x in range(-30, 30)]) for y in range(30, -30, -1)]))
        main()
    except KeyboardInterrupt:
        '''注意:Ctrl+C会在这里企图退出主线程,因为触发Ctrl+C之前可能已经开启了(不确定数量的)子线程(即已经开始执行远程命令),
        故而主线程会等待其子线程退出(并打印结果)后再退出.这种行为是正确的,因为一旦开始执行远程命令,即使关闭了其ssh连接,
        远程server上已开启的命令也不会因此中断,故而应该等待其完成并打印结果.
        '''
        if threading.active_count() > 1:
            OutputText.print_color('\n{}----bye----: waiting for sub_threads exit ...'.format(INDENT_1))
        else:
            OutputText.print_color('\n{}----bye----'.format(INDENT_1))
