#!/usr/bin/env python
# coding:utf-8

import logging
from util.GoKu import singleton

@singleton
class Logging(object):
    def __init__(self, device_name):
        self.device_name = device_name
        self.logger = logging.getLogger('SuperApe-Test')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('./log/' + self.device_name + '.log')
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def getlogger(self):
        return self.logger
