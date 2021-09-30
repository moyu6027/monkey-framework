#!/usr/bin/env python
# coding:utf-8

import sys
sys.path.append('..')
from util.AdbCmd import AdbCmd
from util.ConfParser import ConfParser
import random
from util.Logging import Logging
from util.GoKu import *
from util.AppInfo import AppInfo
from util.FileUtil import *
from monkeyutil.Monitor import *
from platform import uname

system = uname().system

CRASH = 'CRASH '
ANR = 'ANR |anr '
excep = 'Exception'
NoResponse = 'NOT RESPONDING'
keyword = [CRASH, ANR, excep, NoResponse]
logcat_keyword = {
    'crash': '-b crash',
    'all_exception': '-e "ANR|anr|Exception|NO RESPONDING|error|Error|NOT RESPONDING|Fatal" *:E',
    'GC': '-e "GC "',
    'watchdog': '-e "WATCHDOG"'
}
Monkeyfinished = '// Monkey finished'
NullPointer = "java.lang.NullPointerException"
IllegalState = "java.lang.IllegalStateException"
IllegalArgument = "java.lang.IllegalArgumentException"
ArrayIndexOutOfBounds = "java.lang.ArrayIndexOutOfBoundsException"
RuntimeException = "java.lang.RuntimeException"
SecurityException = "java.lang.SecurityException"


class Run(object):
    def __init__(self, device_name):
        self.device_name = device_name
        self.output = OutputText()
        self.logger = Logging(device_name).getlogger()
        self.output.write_or_print('\n{}----{}\n'.format(OutputText.INDENT_1, device_name), color=33)
        self.log_device_path = './outres/' + self.device_name + "/log/"
        write_file('./log/' + self.device_name + '.log', '\n{}----{}\n'.format(OutputText.INDENT_1, device_name),
                   is_cover=True)
        write_file(self.log_device_path + self.device_name + '.log',
                   '\n{}----{}\n'.format(OutputText.INDENT_1, device_name),
                   is_cover=True)
        self.conf = ConfParser(device_name).parser('yml')
        self.device_id = self.conf.get('device')
        write_file(self.log_device_path + self.device_name + '_info.log',
                   '{}={}\n'.format("device", self.device_id), is_cover=True)
        self.package = self.conf.get('package')
        self.windows = self.conf.get('windows')
        self.monitor_folder = 'monkey-monitor'
        self.adbCmd = AdbCmd(self.device_id)

    """连接设备"""

    def create_connection(self):
        if ":" in self.device_id:
            cmd = "adb connect " + self.device_id
            self.output.write_or_print('{}connect {}\n'.format(OutputText.INDENT_2, self.device_id), color=33)
            try:
                result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE).stdout.read().decode()
                if result is 'connected to ' + self.device_id or 'already connected' in result:
                    self.output.write_or_print('{}message is: {}'.format(OutputText.INDENT_2, result), color=33)
                    return True
                else:
                    self.output.write_or_print('{}device connect fail\n'.format(OutputText.INDENT_2), color=32)
                    self.output.print_lock()
                    return False
            except TimeoutError as e:
                self.output.write_or_print('{}device connect error: {}\n'.format(OutputText.INDENT_2, e), color=31)
                self.output.print_lock()
                return 'continue'
            except Exception as e:
                self.output.write_or_print('{}device connect error: {}\n'.format(OutputText.INDENT_2, e), color=31)
                self.output.print_lock()
                return False
        else:
            return True

    def make_env(self):
        """
        init env
        :return:
        """
        adb_command = AdbCmd(self.device_id)
        # kill process
        adb_command.kill_pid('com.android.commands.monkey')
        # push service file
        # adb_command.shell('mkdir /sdcard/superape')
        # adb_command.push('./conf/preAction.json', '/sdcard/superape/')
        # push file
        # adb_command.push('./libs/monkey-debug.jar', '/sdcard/')
        adb_command.push('./libs/ape-v1.0.0.jar', '/sdcard/')
        adb_command.push_enhance('./libs/busybox', '/data/local/tmp/')
        adb_command.push('./libs/monitor.sh', '/data/local/tmp/')
        adb_command.shell('chmod 777 /data/local/tmp/busybox')
        # Increase execution authority
        adb_command.shell('chmod 777 /data/local/tmp/monitor.sh')

        # ape service init
        adb_command.shell('settings put secure enabled_accessibility_services hcc.monkey.smartape/.MonkeyService')
        # unlock screen
        adb_command.unlock_screen()
        # disable ime
        # adb_command.disable_ime('com.sec.android.inputmethod/.SamsungKeypad')
        '''隐藏相应app的导航栏状态栏'''
        adb_command.hideSetting(self.package)
        # clear logcat
        adb_command.adb('logcat --clear')

    def get_info(self):
        """
        获取app信息
        """
        gb = AppInfo(self.package, self.device_name, self.device_id)
        gb.get_app_version()
        gb.get_android_version()
        gb.get_device_info()

    def tear_down(self):
        """
        clear env
        :return:
        """
        self.adbCmd.kill_pid("trace_pipe")
        self.adbCmd.shell('touch /data/local/tmp/stop')
        self.logger.info("=" * 25 + "stop monitor" + "=" * 25)
        time.sleep(1)
        self.adbCmd.pull('/data/local/tmp/' + self.monitor_folder, './outres/' + self.device_name + '/')
        self.adbCmd.pull('/data/anr/', './outres/' + self.device_name + '/')
        self.adbCmd.pull('/sdcard/monkey-out/', './outres/' + self.device_name + '/')

    def launch_monitor(self, pid):
        """
        launch monitor script
        :return:
        """
        # shell parameter $1 -- $5
        montior_folder = self.monitor_folder
        montiorWindow = self.package
        if self.windows is not None:
            montiorWindow = self.package+'/'+self.windows + '[' + pid + ']' + '#0'
        monitorPackages = self.package
        monitor_interval = 2
        meminfo_type = 1
        cmd = f'sh /data/local/tmp/monitor.sh {montior_folder} {montiorWindow} {monitorPackages} {monitor_interval} {meminfo_type} &'
        self.logger.info(cmd)
        self.adbCmd.shell(cmd)
        self.logger.info("=" * 25 + "start monitor" + "=" * 25)

    def logcatCollect(self):
        """
        logcat collection
        """
        logcatPathList = []
        logcatFileList = []
        run_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        for key, value in logcat_keyword.items():
            logcat_cmd = 'adb -s {} logcat -v long {}'.format(self.device_id, value)
            logcat_path = os.path.join(
                self.log_device_path + self.device_name + '_' + key.strip() + '_logcat_' + run_time + '.log')
            logcat_log = open(logcat_path, 'a')
            logcatPathList.append(logcat_path)
            logcatFileList.append(logcat_log)
            subprocess.Popen(logcat_cmd, shell=True, stdout=logcat_log, stderr=subprocess.STDOUT)
        return logcatPathList, logcatFileList

    # @pysnooper.snoop(prefix='MonkeyTest || ')
    @timer
    # @profiler
    def run_command(self):
        """
        执行monkey测试的流程
        """
        '''prepare env file'''
        self.make_env()
        '''获取apk信息'''
        self.get_info()
        write_file(self.log_device_path + self.device_name + '_info.log',
                   '{}={}\n'.format("start_time", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))))
        '''开启logcat 日志'''
        logcatPathList, logcatFileList = self.logcatCollect()
        '''组织command'''
        ape_command = self.monkey_cmd(self.conf)

        # if '--act-whitelist-file' in ape_command:
        ape_command = 'adb -s {} shell CLASSPATH=/sdcard/{} exec app_process /system/bin ' \
                      'monkey.hccn.com.ape.Monkey '.format(self.device_id, 'ape-v1.0.0.jar') \
                      + ape_command + ''
        # else:
        #     ape_command = 'adb -s {} shell CLASSPATH=/sdcard/{} exec app_process /system/bin ' \
        #                   'monkey.jt.com.monkeydemo.Monkey '.format(self.device_id, 'monkey-debug.jar') \
        #                   + ape_command + ''
        log_path = os.path.join(self.log_device_path + self.device_name + '.log')
        device_log = open(log_path, 'a')
        self.logger.info('SuperApe CMD === {}'.format(ape_command))
        subprocess.Popen(ape_command, shell=True, stdout=device_log, stderr=subprocess.STDOUT)
        time.sleep(1)
        pid = self.adbCmd.getPid(self.package)
        '''launch monitor script'''
        self.launch_monitor(pid)
        is_running = True
        time.sleep(2)
        while is_running:
            if self.adbCmd.find_pid('com.android.commands.monkey'):
                self.logger.info("=" * 25 + "Monkey is running..." + "=" * 25)
            else:
                is_running = False
                device_log.close()

                for i in range(4):
                    self.adbCmd.kill_pid_list('logcat')
                for p in logcatFileList:
                    p.close()
                self.tear_down()
                write_file(self.log_device_path + self.device_name + '_info.log',
                           '{}={}\n'.format("end_time",
                                            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))))
                self.logger.info("=" * 25 + "Monkey is Stopped!!!" + "=" * 25)
        time.sleep(1)

        '''analysis csv and generate html report'''
        pathDict = {
            'templatePath': os.path.abspath('./monkeyutil/monitor_HTML'),
            'monitorDataPath': os.path.abspath('./outres/' + self.device_name + '/monkey-monitor'),
            'logcatPath': logcatPathList,
            'deviceLogPath': log_path
        }
        monitorRun(pathDict)

    @staticmethod
    def monkey_cmd(conf_dict):
        """
        拼接解析后的monkey 命令
        :param conf_dict:
        :return:
        """
        cmd = '-p ' + conf_dict.get('package') + " "

        # 格式化Log等级，一个-v最低，三个-v最高
        if conf_dict.get('log_level') is 3:
            cmd += '-v -v -v '
        elif conf_dict.get('log_level') is 2:
            cmd += '-v -v '
        else:
            cmd += '-v '

        # If you 're-run' the Monkey with the same seed value,
        # it will generate the same sequence of events.
        if conf_dict.get('seed') is False:
            pass
        else:
            cmd += '-s ' + str(random.randint(100, 100000)) + " "

        # format time interval between events
        if conf_dict.get('throttle') is False:
            pass
        else:
            cmd += '--throttle ' + str(conf_dict.get('throttle')) + " "

        # Black/white list, white list with a higher priority.
        if conf_dict.get('activity-whitelist') is True:
            push_white = 'adb push ./conf/whitelist.txt /sdcard/whitelist.txt'
            if os.system(push_white) == 0:
                cmd += '--act-whitelist-file /sdcard/whitelist.txt '
        elif conf_dict.get('activity-blacklist') is True:
            push_black = 'adb push ./conf/blacklist.txt /sdcard/blacklist.txt'
            if os.system(push_black) == 0:
                cmd += '--act-blacklist-file /sdcard/blacklist.txt '

        # mix mode switch
        if conf_dict.get('mix') is False:
            pass
        else:
            cmd += '--mix '

        # ignore switch
        if conf_dict.get('skip-err') is False:
            pass
        else:
            cmd += '--ignore-crashes --ignore-timeouts --ignore-security-exceptions --ignore-native-crashes --monitor-native-crashes '

        # format monkey event
        if conf_dict.get('running-events') is False:
            pass
        else:
            cmd += str(conf_dict.get('running-events')) + " "

        # format monkey running time (unit minutes)
        if conf_dict.get('running-minutes') is False:
            pass
        else:
            cmd += str(conf_dict.get('running-minutes')) + " "

        if conf_dict.get('bugreport') is False:
            pass
        else:
            cmd += '--bugreport '

        if conf_dict.get('hprof') is False:
            pass
        else:
            cmd += '--hprof '

        return cmd
