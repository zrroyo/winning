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


class Draw:
    """画蜡烛图"""
    def __init__(self, sql_conn, dbg=False):
        self.debug = Debug('Draw', dbg)
        self.sql_conn = sql_conn

    def to_trade_date(self, contract, timestamp):
        """将交易时间戳转换为对应的交易日"""
        _date = (timestamp + pd.to_timedelta("3h")).date()
        strSql = "SELECT Time FROM %s_dayk WHERE Time >= '%s' LIMIT 1" % (contract, _date)
        values = pd.read_sql(strSql, self.sql_conn)
        return values.iloc[0]['Time']

    def _drawPositionLine(self, transactions, tradeId, pos, xticks, xlables, values, open_date, close_date):
        """绘制持仓趋势线
        :param tradeId: 交易id
        :param pos: 仓位，'OP1', 'OP2', 'OP3', 'OP4', 'OP5'
        :return: None
        """
        trans = transactions
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

    def drawCandlestick(self, dat_table, periods, title, pic_path, position, show, grid, transactions=None):
        """画蜡烛图
        :param dat_table: 蜡烛图数据源
        :param periods: 时间区间
        :param title: 图标题
        :param pic_path: 图片保存路径
        :param position: 需绘制的仓位
        :param show: 显示图片
        :param grid: 显示网格线
        :return: None
        """
        contract = dat_table.split('_')
        contract = contract[0]
        clause = ''
        if periods:
            if periods[0]:
                _start_date = self.to_trade_date(contract, periods[0])
                clause += "Time >= '%s'" % _start_date
            if periods[1]:
                _close_date = self.to_trade_date(contract, periods[1])
                if clause:
                    clause += " AND "
                clause += "Time <= '%s'" % _close_date
            if clause:
                clause = "WHERE " + clause

        strSql = "SELECT Time, Open, Close, High, Low FROM %s %s" % (dat_table, clause)
        values = pd.read_sql(strSql, self.sql_conn)
        xtkLables = map(lambda x: str(x), list(values['Time']))
        _xtkFirst = date2num(values.iloc[0]['Time'])
        # 消除周末、节假日时间间隔影响，保持紧邻显示
        xticks = np.arange(_xtkFirst, _xtkFirst + len(values), 1)
        values['Time'] = xticks
        _values = values.values

        # 中文显示
        plt.rcParams['font.sans-serif'] = 'simhei'
        plt.rcParams['font.family'] = 'sans-serif'
        # 窗口大小
        fig_width = 0.2 * len(values)  # 每格0.2寸
        fig_height = 6 if position else 12
        plt.figure(figsize = (fig_width, fig_height))
        fig = plt.gcf()
        fig.add_subplot()
        ca = plt.gca()
        ca.set_title(title)
        # 设置离底端距离，预留X轴标题设置空间
        fig.subplots_adjust(left = 0.2, bottom = 0.2)
        ca.xaxis_date()
        # 设置X轴刻度标签为显示时间
        rotation = 60 if position else 90
        plt.xticks(xticks, rotation = rotation)
        ca.set_xticklabels(xtkLables)
        plt.ylabel(u"价格（元）")
        # plt.xlabel(u"时间")
        # 绘图
        mpf.candlestick_ochl(ca, _values, width = 1, colorup = 'red', colordown = 'green')
        # 收盘价趋势线
        plt.plot(xticks, list(values['Close']), "m--")
        # 绘制持仓线
        if position:
            trd_id, _ = title.split(' ')
            self._drawPositionLine(transactions, trd_id, position, xticks, xtkLables, list(values['Close']),
                                _start_date, _close_date)

        # 设置Max、Min标签
        _max = values[values.High == max(values.High)].head(1)
        _min = values[values.Low == min(values.Low)].head(1)
        # 增大y轴以放置Max、Min标签
        _ylim = plt.ylim()
        plt.ylim(_ylim[0]-40, _ylim[1]+40)
        plt.annotate("Max: %s" % int(_max.High), xy = (xticks[_max.index[0]], _max.High+1),
            xytext = (xticks[_max.index[0]], _max.High+20),
            arrowprops = dict(arrowstyle = '->', connectionstyle = "arc3,rad=.2"))
        plt.annotate("Min: %s" % int(_min.Low), xy = (xticks[_min.index[0]], _min.Low-1),
            xytext = (xticks[_min.index[0]], _min.Low-20),
            arrowprops = dict(arrowstyle = '->', connectionstyle = "arc3,rad=.2"))

        # 添加网格线
        if grid:
            plt.grid(True)
        # 保存图片
        fig.set_size_inches(max(fig_width, 2.5), fig_height)
        _filename = title.replace(' ', '_')
        fig.savefig(os.path.join(pic_path, _filename), bbox_inches='tight', dpi=200)
        if show:
            plt.show()


class DrawPosCharts:
    """画图持仓蜡烛图"""
    def __init__(self, path, dbg=False):
        self.debug = Debug('DrawPosCharts', dbg)
        self.sql = SQL()
        self.sql.connect("history2")
        if not path:
            raise DrawChartsError("Please specify the path in which test data are stored!")
        self.work_path = os.path.join(os.getcwd(), "TESTDATA", path)
        self.transactions = pd.read_excel(os.path.join(self.work_path, "TRANSACTIONS.xlsx"))

    def _draw(self, todo, position, show, grid, subdir = None):
        """画图
        :param todo: 交易列表，用逗号分隔
        :param position: 需绘制的仓位
        :param show: 显示图片
        :param grid: 显示网格线
        :param subdir: 保存图片的子目录
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
            if not os.path.exists(_path):
                os.mkdir(_path)

        prev = None
        values = None
        draw = Draw(self.sql.conn)
        for t in _trans:
            _t = t.split('_')
            _contract = "_".join(_t[0:2])
            if not prev or prev != _contract:
                prev = _contract
                _xls = os.path.join(self.work_path, "%s_TRADE_STAT.xlsx" % _contract)
                values = pd.read_excel(_xls)

            dat_table = "%s_dayk" % _t[0]
            _ticks = values[values.TRD_ID == t][['Tick_Start', 'Tick_End']]
            title = "%s %s" % (t, position)
            draw.drawCandlestick(dat_table, list(_ticks.iloc[0]), title, _path, position, show,
                                 grid, self.transactions)

    def drawOptionsHandler(self, options, argv):
        """命令解析函数
        :param options: 选项集
        :param argv: 命令参数列表
        :return: 成功返回True，否则返回False
        """
        validPos = ['OP1', 'OP2', 'OP3', 'OP4', 'OP5']
        if options.pos not in validPos:
            self.debug.error("validPos: %s" % validPos)
            return False

        if options.select:
            self._draw(options.select, options.pos, options.show, options.grid, options.name)


class DrawCandleCharts:
    """画图持仓蜡烛图"""
    def __init__(self, dbg=False):
        self.debug = Debug('DrawCandleCharts', dbg)
        self.sql = SQL()
        self.sql.connect("history2")

    def _draw(self, wk_path, contracts, ineterval, show, grid, name):
        """画图
        :param wk_path: 工作目录
        :param contracts: 合约列表，以逗号分隔
        :param ineterval: 时间区间
        :param show: 显示图片
        :param grid: 显示网格线
        :param name: 图片名称
        """
        if not os.path.exists(wk_path):
            os.mkdir(wk_path)
            if not os.path.exists(wk_path):
                raise DrawChartsError("Can not make directory: %s" % wk_path)

        draw = Draw(self.sql.conn)
        peroids = []
        if ineterval:
            peroids = ineterval.split(',')
            peroids = [pd.to_datetime(t) for t in peroids]
        _contracts = contracts.split(',')
        for c in _contracts:
            if not c:
                continue
            title = name if name else c
            draw.drawCandlestick(c, peroids, title, wk_path, None, show, grid)

    def drawOptionsHandler(self, options, argv):
        """命令解析函数
        :param options: 选项集
        :param argv: 命令参数列表
        :return: 成功返回True，否则返回False
        """
        wk_path = os.getcwd()
        if options.path:
            wk_path = options.path
        self._draw(wk_path, options.select, options.interval, options.show, options.grid, options.name)


def drawOptionsParser(parser, argv):
    """命令解析入口
    :param parser: OptionParser接口对象
    :param argv: 命令参数列表
    """
    parser.add_option('-p', '--path', dest='path',
            help='Path in which the test data are stored.')
    parser.add_option('-s', '--select', dest='select',
            help='Select a transaction to draw.')
    parser.add_option('-P', '--pos', dest='pos',
            help='Position to draw.')
    parser.add_option('-n', '--name', dest='name',
            help='Name of subdir to store pictures.')
    parser.add_option('-g', '--grid', action="store_true", dest='grid',
            help='Enable grid in pictures.')
    parser.add_option('-S', '--show', action="store_true", dest='show',
            help='Show pictures.')
    parser.add_option('-D', '--debug', action="store_true", dest='debug',
            help='Enable debug mode.')
    parser.add_option('-i', '--interval', dest='interval',
                      help='Only draw the candlesticks within a time interval.')

    (options, args) = parser.parse_args()
    if options.pos:
        draw = DrawPosCharts(options.path, options.debug)
    else:
        draw = DrawCandleCharts(options.debug)
    draw.drawOptionsHandler(options, argv)
