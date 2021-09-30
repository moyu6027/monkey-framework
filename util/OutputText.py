#!/usr/bin/env python
# coding:utf-8

from platform import uname
import threading
from sys import exit, stdout

computer = uname().system
global_lock = threading.Lock()


class OutputText():
    """该类具有write()方法,用来存储每台device的执行结果.
    因为引入了多线程异步执行才需要这么做,以保证异步执行多台device的输出不会乱.
    为了简洁,并行与串行的输出都用这一套东西"""
    INDENT_1 = 0 * ' '
    INDENT_2 = 4 * ' '
    INDENT_3 = 8 * ' '

    def __init__(self):
        self.buffer = []

    def write_or_print(self, *args, color=None, parallel=False):
        """并行模式先缓存最后加锁输出; 串行模式直接输出"""
        # print(args)  # debug 可观察到并行时内部各输出的产生顺序
        if parallel:
            if color and not computer == 'Windows':
                self.buffer.append('\033[0;{}m'.format(color))
                self.buffer.extend(args)
                self.buffer.append('\033[0m')
            else:
                self.buffer.extend(args)
        else:
            for string in args:
                if color and not computer == 'Windows':
                    self.print_color(string, color=color, end='')
                else:
                    print(string, end='')

    def print_lock(self):
        """并发模式下,所有的输出动作都要加锁"""
        if self.buffer:
            with global_lock:
                for line in self.buffer:
                    print(line, end='')

    @staticmethod
    def print_color(text, color=32, sep=' ', end='\n', file=stdout, flush=False):
        """打印彩色字体,color默认为红色
        该方法只针对Linux有效"""
        if computer == 'Windows':
            print(text, sep=sep, end=end, file=file, flush=flush)
        else:
            print('\033[0;{}m'.format(color), end='')
            print(text, sep=sep, end=end, file=file, flush=flush)
            print('\033[0m', end='')
