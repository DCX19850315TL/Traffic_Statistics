#!/usr/bin/env python
#_*_ coding:utf-8 _*_
'''
@author: tanglei
@contact: tanglei_0315@163.com
@file: common.py
@time: 18-10-17 下午4:50
'''
import sys

def LongToInt(value):
    assert isinstance(value, (int, long))
    return int(value & sys.maxint)