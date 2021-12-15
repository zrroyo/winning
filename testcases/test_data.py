#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
sys.path.append('..')
import core.corecfg
from dataMgr.data import *
from globals import GlobalConfig

_global_cfg = GlobalConfig()


def print_data(data, date):
    print "M: %s" % data.M(date, F_CLOSE, 1)
    print "M5: %s" % data.M5(date, F_CLOSE)
    print "M10: %s" % data.M10(date, F_CLOSE)
    print "M20: %s" % data.M20(date, F_CLOSE)
    print "M30: %s" % data.M30(date, F_CLOSE)
    print "Open: %s" % data.getOpen(date)
    print "Close: %s" % data.getClose(date)
    print "Avg: %s" % data.getAvg(date)
    print "High: %s" % data.getHighest(date)
    print "Low: %s" % data.getLowest(date)
    print "Highest Before: exclude %s, not exclude %s" % (
        data.highestWithinDays(date, 10, F_CLOSE), data.highestWithinDays(date, 10, F_CLOSE, False))
    print "Lowest Before: exclude %s, not exclude %s" % (
        data.lowestWithinDays(date, 10, F_CLOSE), data.lowestWithinDays(date, 10, F_CLOSE, False))


def doTestData():
    """Data测试"""
    _contracts_desc_file = os.path.join(_global_cfg.get_config_dir(), 'contracts_desc')  # 默认合约描述文件
    descCfg = core.corecfg.ContractDescConfig(_contracts_desc_file)
    data = Data('p1405', descCfg, False)

    date = '2014-03-11'
    print "Test Middle: Date: %s" % date
    print_data(data, date)

    date = '2013-05-16'
    print "Test Left Bound: Date: %s" % date
    print_data(data, date)

    date = '2014-04-30'
    print "Test Right Bound: Date: %s" % date
    print_data(data, date)

    """
    Test Middle: Date: 2014-03-11s
    M: 6404.0
    M5: 6308.0
    M10: 6222.4
    M20: 6129.9
    M30: 6014.93333333
    Open: 6280.0
    Close: 6404.0
    Avg: 6334.0
    High: 6430.0
    Low: 6230.0
    Highest Before: exclude 6328.0, not exclude 6404.0
    Lowest Before: exclude 6102.0, not exclude 6102.0
    Test Left Bound: Date: 2013-05-16
    M: 6298.0
    M5: 6298.0
    M10: 6298.0
    M20: 6298.0
    M30: 6298.0
    Open: 6246.0
    Close: 6298.0
    Avg: 6274.0
    High: 6326.0
    Low: 6232.0
    Highest Before: exclude None, not exclude 6298.0
    Lowest Before: exclude None, not exclude 6298.0
    Test Right Bound: Date: 2014-04-30
    M: 5876.0
    M5: 5912.0
    M10: 5930.4
    M20: 5963.6
    M30: 6001.73333333
    Open: 5898.0
    Close: 5876.0
    Avg: 5882.0
    High: 5898.0
    Low: 5876.0
    Highest Before: exclude 6002.0, not exclude 6002.0
    Lowest Before: exclude 5900.0, not exclude 5876.0
    """


def doTestDataMink():
    """DataMink测试"""
    _contracts_desc_file = os.path.join(_global_cfg.get_config_dir(), 'contracts_desc')  # 默认合约描述文件
    descCfg = core.corecfg.ContractDescConfig(_contracts_desc_file)
    data = DataMink('p1405_mink', descCfg, False)

    date = DataMink.dateConverter('2014-03-11 14:36:00')
    print "Test Middle: Date: %s" % date
    print_data(data, date)

    date = DataMink.dateConverter('2013-05-16 9:01:00')
    print "Test Left Bound: Date: %s" % date
    print_data(data, date)

    date = DataMink.dateConverter('2014-04-30 14:58:00')
    print "Test Right Bound: Date: %s" % date
    print_data(data, date)

    """
    Test Middle: Date: 2014-03-11 14:36:00
    M: 6398.0
    M5: 6306.8
    M10: 6221.8
    M20: 6129.6
    M30: 6014.73333333
    Open: 6400.0
    Close: 6398.0
    Avg: 0.0
    High: 6402.0
    Low: 6398.0
    Highest Before: exclude 6328.0, not exclude 6398.0
    Lowest Before: exclude 6102.0, not exclude 6102.0
    Test Left Bound: Date: 2013-05-16 09:01:00
    M: 6246.0
    M5: 6246.0
    M10: 6246.0
    M20: 6246.0
    M30: 6246.0
    Open: 6246.0
    Close: 6246.0
    Avg: 0.0
    High: 6246.0
    Low: 6246.0
    Highest Before: exclude None, not exclude 6246.0
    Lowest Before: exclude None, not exclude 6246.0
    Test Right Bound: Date: 2014-04-30 14:58:00
    M: 5876.0
    M5: 5912.0
    M10: 5930.4
    M20: 5963.6
    M30: 6001.73333333
    Open: 5878.0
    Close: 5876.0
    Avg: 0.0
    High: 5878.0
    Low: 5876.0
    Highest Before: exclude 6002.0, not exclude 6002.0
    Lowest Before: exclude 5900.0, not exclude 5876.0
    """


def doTestDatamink_NightTrade():
    """夜盘DataMink测试"""
    _contracts_desc_file = os.path.join(_global_cfg.get_config_dir(), 'contracts_desc')  # 默认合约描述文件
    descCfg = core.corecfg.ContractDescConfig(_contracts_desc_file)
    data = DataMink('p1701_mink', descCfg, False)

    date = DataMink.dateConverter('2016-04-07 14:36:00')  # 白天时段
    print "Test Middle: Date: %s" % date
    print_data(data, date)

    date = DataMink.dateConverter('2016-04-07 21:15:00')  # 夜晚时段
    print "Test Middle: Date: %s" % date
    print_data(data, date)

    data = Data('p2201', descCfg, False)
    # date = DataMink.dateConverter('2021-10-21')
    date = DataMink.dateConverter('2021-12-1')
    print "Test Middle: Date: %s" % date
    print "M: %s" % data.M(date, F_CLOSE, 1)
    print "M5: %s" % data.M5(date, F_CLOSE)
    print "M10: %s" % data.M10(date, F_CLOSE)
    print "M20: %s" % data.M20(date, F_CLOSE)
    print "M60: %s" % data.M60(date, F_CLOSE)
    print "Open: %s" % data.getOpen(date)
    print "Close: %s" % data.getClose(date)
    print "Avg: %s" % data.getAvg(date)
    print "High: %s" % data.getHighest(date)
    print "Low: %s" % data.getLowest(date)
    print "Highest Before: exclude %s, not exclude %s" % (
        data.highestWithinDays(date, 10, F_CLOSE), data.highestWithinDays(date, 10, F_CLOSE, False))
    print "Lowest Before: exclude %s, not exclude %s" % (
        data.lowestWithinDays(date, 10, F_CLOSE), data.lowestWithinDays(date, 10, F_CLOSE, False))

    """
    Test Middle: Date: 2016-04-07 14:36:00
    M: 5428.0
    M5: 5440.8
    M10: 5417.8
    M20: 5323.0
    M30: 5191.8
    Open: 5428.0
    Close: 5428.0
    Avg: 0.0
    High: 5428.0
    Low: 5428.0
    Backend Qt5Agg is interactive backend. Turning interactive mode on.
    Highest Before: exclude 5480.0, not exclude 5480.0
    Lowest Before: exclude 5302.0, not exclude 5302.0
    Test Middle: Date: 2016-04-07 21:15:00
    M: 5384.0
    M5: 5436.4
    M10: 5426.8
    M20: 5340.5
    M30: 5209.8
    Open: 5400.0
    Close: 5384.0
    Avg: 0.0
    High: 5402.0
    Low: 5382.0
    Highest Before: exclude 5480.0, not exclude 5480.0
    Lowest Before: exclude 5386.0, not exclude 5384.0
    Test Middle: Date: 2021-12-01 00:00:00
    M: 9258.0
    M5: 9398.8
    M10: 9551.8
    M20: 9467.5
    M60: 9136.3
    Open: 9046.0
    Close: 9258.0
    Avg: 0.0
    High: 9294.0
    Low: 9002.0
    Highest Before: exclude 9978.0, not exclude 9978.0
    Lowest Before: exclude 9146.0, not exclude 9146.0
    """

if __name__ == '__main__':
    doTestData()
    doTestDataMink()
    doTestDatamink_NightTrade()
