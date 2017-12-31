#-*- coding:utf-8 -*-

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
import matplotlib.finance as mpf
from matplotlib.pylab import date2num

from misc.debug import Debug
from misc.execcmd import ExecCommand
from db.sql import SQL

# 默认关闭debug信息
debug = Debug('Draw', False)
# shell命令执行接口
shell = ExecCommand()


def drawCandlestick(conn, contract, periods, title, path, show):
	"""
	画蜡烛图
	:param conn: 数据库句柄
	:param contract: 合约名
	:param periods: 时间区间
	:param title: 图标题
	:param path: 图片保存路径
	:param show: 显示图片
	:return: None
	"""
	# 可直接获取Timestamp中的日期
	_start = periods[0]._date_repr
	_end = periods[1]._date_repr

	strSql = "SELECT Time, Open, Close, High, Low FROM %s_dayk " \
		"WHERE Time >= '%s' and Time <= '%s'" % (contract, _start, _end)
	values = pd.read_sql(strSql, conn)
	xtkLables = map(lambda x: str(x), list(values['Time']))
	_xtkFirst = date2num(values.iloc[0]['Time'])
	# 消除周末、节假日时间间隔影响，保持紧邻显示
	xticks = np.arange(_xtkFirst, _xtkFirst + len(values), 1)
	values['Time'] = xticks
	_values = values.as_matrix()

	# 中文显示
	plt.rcParams['font.sans-serif'] = 'simhei'
	plt.rcParams['font.family'] = 'sans-serif'
	# 窗口大小，每格0.4寸
	_width = 0.4 * (len(values) + 1)
	plt.figure(figsize = (_width, 7))
	fig = plt.gcf()
	fig.add_subplot()
	ca = plt.gca()
	ca.set_title(title)
	# 设置离底端距离，预留X轴标题设置空间
	fig.subplots_adjust(bottom=0.2)
	ca.xaxis_date()
	# 设置X轴刻度标签为显示时间，并倾斜60度
	plt.xticks(xticks, rotation = 60)
	ca.set_xticklabels(xtkLables)
	plt.ylabel(u"价格（元）")
	plt.xlabel(u"时间")
	# 绘图
	mpf.candlestick_ochl(ca, _values, width = 1, colorup = 'red', colordown = 'green')
	# 收盘价趋势线
	plt.plot(xticks, list(values['Close']), "b-")

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
	# # 添加网格线后看不清楚影线
	# plt.grid(True)
	fig.set_size_inches(_width, 7)
	fig.savefig(os.path.join(path, "%s.png" % title))
	if show:
		plt.show()


def draw(path, transactions, show):
	"""
	画图
	:param path: 数据路径
	:param transactions: 交易列表，用逗号分隔
	:param show: 显示图片
	:return: None
	"""
	sql = SQL()
	sql.connect("history2")

	_trans = transactions.split(',')
	for t in _trans:
		_t = t.split('_')
		xls = "_".join(_t[0:2])
		_path = os.path.join(os.getcwd(), "TESTDATA", path)
		xls = os.path.join(_path, "%s_TRADE_STAT.xlsx" % xls)
		values = pd.read_excel(xls)
		values = values[values.TRD_ID == t][['Tick_Start', 'Tick_End']]
		drawCandlestick(sql.conn, _t[0], list(values.iloc[0]), t, _path, show)


def drawOptionsHandler(options, argv):
	"""
	命令解析函数
	:param options: 选项集
	:param argv: 命令参数列表
	:return: 成功返回True，否则返回False
	"""
	if options.debug:
		global debug
		debug = Debug('Draw', True)

	if not options.path:
		debug.error("Please specify the path in which test data are stored.")
		return False

	if options.draw:
		draw(options.path, options.draw, options.show)


def drawOptionsParser(parser, argv):
	"""
	命令解析入口
	:param parser: OptionParser接口对象
	:param argv: 命令参数列表
	"""
	parser.add_option('-p', '--path', dest='path',
			help='Path in which the test data are stored.')
	parser.add_option('-d', '--draw', dest='draw',
			help='Draw the candlestick chart for a transaction.')
	parser.add_option('-s', '--show', action="store_true", dest='show',
			help='Show pictures.')
	parser.add_option('-D', '--debug', action="store_true", dest='debug',
			help='Enable debug mode.')

	(options, args) = parser.parse_args()
	drawOptionsHandler(options, argv)
