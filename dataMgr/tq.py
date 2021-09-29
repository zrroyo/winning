# -*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: Tue Sep 28 00:17:48 CST 2021
"""

from datetime import datetime
from importer import Import


class TQImporter(Import):
    """天勤数据导入数据库接口"""
    def fileRecordToColumns(self, line):
        """将文件数据记录转换成字段列表"""
        time, open, high, low, close, volume, open_oi, close_oi = line.rstrip('\r\n').split(',')
        avg = 0
        return time, open, high, low, close, avg, volume, open_oi

    def get_time_format(self):
        """时间格式字符串"""
        return '%Y-%m-%d %H:%M:%S'

    def formatTime(self, time):
        """格式化时间"""
        _time = self.trans_time(time)
        return datetime.strftime(_time, self.get_time_format())

    def trans_time(self, time):
        _time, _ = time.split('.')
        return datetime.strptime(_time, self.get_time_format())

    def recordsFileToTable(self, file):
        """把数据文件转换为数据表名"""
        symbol, tm_type = file.split('_')
        _, symbol = symbol.split('.')
        ret = symbol
        if tm_type.startswith('60'):
            ret += '_mink'
        elif tm_type.startswith('86400'):
            ret += '_dayk'
        return ret
