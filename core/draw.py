# -*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2017年 12月 23日 星期六 13:30:32 CST

绘图模块
"""

import os
import sys
sys.path.append(".")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mpl_finance as mpf
from matplotlib.pylab import date2num
from pandas.plotting import register_matplotlib_converters
from misc.debug import Debug
from db.sql import SQL

register_matplotlib_converters()


class DrawChartsError(Exception):
    """画图错误"""
    pass


class DrawCharts:
    """画图，蜡烛图等"""
    def __init__(self, path, dbg=False):
        self.debug = Debug('Draw', dbg)
        self.sql = SQL()
        self.sql.connect("history2")
        if not path:
            raise DrawChartsError("Please specify the path in which test data are stored!")
        self.work_path = os.path.join(os.getcwd(), "TESTDATA", path)
        self.transactions = pd.read_excel(os.path.join(self.work_path, "TRANSACTIONS.xlsx"))

    def to_trade_date(self, contract, timestamp):
        """将交易时间戳转换为对应的交易日"""
        _date = (timestamp + pd.to_timedelta("3h")).date()
        strSql = "SELECT Time FROM %s_dayk WHERE Time >= '%s' LIMIT 1" % (contract, _date)
        values = pd.read_sql(strSql, self.sql.conn)
        return values.iloc[0]['Time']

    def _drawPositionLine(self, tradeId, pos, xticks, xlables, values, open_date, close_date):
        """绘制持仓趋势线
        :param tradeId: 交易id
        :param pos: 仓位，'OP1', 'OP2', 'OP3', 'OP4', 'OP5'
        :return: None
        """
        trans = self.transactions
        posInfo = trans[(trans['TRD_ID'] == tradeId) & (trans["%s_FR_Max" % pos].notnull())]\
            [["%s_OP_TICK" % pos, "%s_OP_PRICE" % pos, "%s_CLS_TICK" % pos, "%s_CLS_PRICE" % pos]]

        for val in posInfo.values:
            _start = xlables.index(str(open_date))
            _end = xlables.index(str(close_date))
            _xticks = xticks[_start : _end+1]
            _yVal = values[_start : _end+1]
            _yVal[0] = val[1]
            _yVal[-1] = val[3]
            plt.plot(_xticks, _yVal, "bo-")

    def _drawCandlestick(self, contract, periods, title, pic_path, position, show, grid):
        """画蜡烛图
        :param contract: 合约名
        :param periods: 时间区间
        :param title: 图标题
        :param pic_path: 图片保存路径
        :param position: 需绘制的仓位
        :param show: 显示图片
        :param grid: 显示网格线
        :return: None
        """
        # 可直接获取Timestamp中的日期
        _start_date = self.to_trade_date(contract, periods[0])
        _close_date = self.to_trade_date(contract, periods[1])

        strSql = "SELECT Time, Open, Close, High, Low FROM %s_dayk " \
            "WHERE Time >= '%s' and Time <= '%s'" % (contract, _start_date, _close_date)
        values = pd.read_sql(strSql, self.sql.conn)
        xtkLables = map(lambda x: str(x), list(values['Time']))
        _xtkFirst = date2num(values.iloc[0]['Time'])
        # 消除周末、节假日时间间隔影响，保持紧邻显示
        xticks = np.arange(_xtkFirst, _xtkFirst + len(values), 1)
        values['Time'] = xticks
        _values = values.values

        # 中文显示
        plt.rcParams['font.sans-serif'] = 'simhei'
        plt.rcParams['font.family'] = 'sans-serif'
        # 窗口大小，每格0.4寸
        _width = 0.3 * (len(values) + 1)
        plt.figure(figsize = (_width, 6))
        fig = plt.gcf()
        fig.add_subplot()
        ca = plt.gca()
        ca.set_title("%s %s" % (title, position))
        # 设置离底端距离，预留X轴标题设置空间
        fig.subplots_adjust(bottom = 0.2)
        ca.xaxis_date()
        # 设置X轴刻度标签为显示时间，并倾斜60度
        plt.xticks(xticks, rotation = 60)
        ca.set_xticklabels(xtkLables)
        plt.ylabel(u"价格（元）")
        plt.xlabel(u"时间")
        # 绘图
        mpf.candlestick_ochl(ca, _values, width = 1, colorup = 'red', colordown = 'green')
        # 收盘价趋势线
        plt.plot(xticks, list(values['Close']), "m--")
        # 绘制持仓线
        if position:
            self._drawPositionLine(title, position, xticks, xtkLables, list(values['Close']),
                                _start_date, _close_date)

        # 设置Max、Min标签
        _max = values[values.High == max(values.High)].head(1)
        _min = values[values.Low == min(values.Low)].head(1)
        # 增大y轴以放置Max、Min标签
        _ylim = plt.ylim()
        plt.ylim(_ylim[0]-40, _ylim[1]+20)
        plt.annotate("Max: %s" % int(_max.High), xy = (xticks[_max.index[0]], _max.High+1),
            xytext = (xticks[_max.index[0]], _max.High+30),
            arrowprops = dict(arrowstyle = '->', connectionstyle = "arc3,rad=.2"))
        plt.annotate("Min: %s" % int(_min.Low), xy = (xticks[_min.index[0]], _min.Low-1),
            xytext = (xticks[_min.index[0]], _min.Low-30),
            arrowprops = dict(arrowstyle = '->', connectionstyle = "arc3,rad=.2"))

        # 添加网格线
        if grid:
            plt.grid(True)
        # 保存图片
        fig.set_size_inches(_width, 6)
        fig.savefig(os.path.join(pic_path, "%s_%s.png" % (title, position)))
        if show:
            plt.show()

    def _draw(self, todo, position, show, grid, subdir = None):
        """画图
        :param todo: 交易列表，用逗号分隔
        :param position: 需绘制的仓位
        :param show: 显示图片
        :param grid: 显示网格线
        :param subdir: 保存图片的子目录
        :return: None
        """
        _trans = todo.split(',')
        # 支持用 T:win/lose 的形式动态选择交易列表
        if todo.startswith("T:"):
            _type = todo[2:]
            field = "%s_PROFIT" % position
            _dt = self.transactions
            if _type == "win":
                _transTmp = _dt[(_dt[field] >= 0) & (_dt[field].notnull())]
            elif _type == "lose":
                _transTmp = _dt[(_dt[field] < 0) & (_dt[field].notnull())]
            else:
                raise DrawChartsError("Found unknown type %s" % _type)

            _trans = list(_transTmp['TRD_ID'].unique())

        _path = self.work_path
        # 创建子目录保存图片
        if subdir:
            _path = os.path.join(_path, subdir)
            try:
                os.mkdir(_path)
            except OSError, e:
                pass

        prev = None
        values = None
        for t in _trans:
            _t = t.split('_')
            _contract = "_".join(_t[0:2])
            if not prev or prev != _contract:
                prev = _contract
                _xls = os.path.join(self.work_path, "%s_TRADE_STAT.xlsx" % _contract)
                values = pd.read_excel(_xls)

            _ticks = values[values.TRD_ID == t][['Tick_Start', 'Tick_End']]
            self._drawCandlestick(_t[0], list(_ticks.iloc[0]), t, _path, position, show, grid)

    def drawOptionsHandler(self, options, argv):
        """命令解析函数
        :param options: 选项集
        :param argv: 命令参数列表
        :return: 成功返回True，否则返回False
        """
        validPos = ['OP1', 'OP2', 'OP3', 'OP4', 'OP5']
        if options.pos and options.pos not in validPos:
            self.debug.error("validPos: %s" % validPos)
            return False

        if options.draw:
            self._draw(options.draw, options.pos, options.show, options.grid, options.name)


def drawOptionsParser(parser, argv):
    """命令解析入口
    :param parser: OptionParser接口对象
    :param argv: 命令参数列表
    """
    parser.add_option('-p', '--path', dest='path',
            help='Path in which the test data are stored.')
    parser.add_option('-d', '--draw', dest='draw',
            help='Draw the candlestick chart for a transaction.')
    parser.add_option('-P', '--pos', dest='pos',
            help='Position to draw.')
    parser.add_option('-n', '--name', dest='name',
            help='Name of subdir to store pictures.')
    parser.add_option('-g', '--grid', action="store_true", dest='grid',
            help='Enable grid in pictures.')
    parser.add_option('-s', '--show', action="store_true", dest='show',
            help='Show pictures.')
    parser.add_option('-D', '--debug', action="store_true", dest='debug',
            help='Enable debug mode.')

    (options, args) = parser.parse_args()
    draw = DrawCharts(options.path, options.debug)
    draw.drawOptionsHandler(options, argv)
