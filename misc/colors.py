#! /usr/bin/env python
# -*- coding:utf-8 -*-

"""
Copyright 2014 Meizu Co., Ltd.
Author: Zhengwang Ruan <zhengwang.ruan@gmail.com>
Start: 2014年 03月 18日 星期二 16:29:12 CST

This program is provided under the Gnu General Public License (GPL)
version 2 ONLY.

颜色模块：
	*定义普通颜色（值）。
	*定义log输出颜色（值）。
"""

COLOR_MAP = {
	'red'	: '\033[0;31m',
	'green'	: '\033[0;32m',
	'blue'	: '\033[0;34m',
	'yellow': '\033[1;33m',
	'purple': '\033[0;35m',
	'black'	: '\033[0;30m',
	'brown'	: '\033[0;33m',
	'white'	: '\033[1;37m',
	'cyan'	: '\033[0;36m',
	}


class Color:
	"""
	颜色类
	"""
	def red(self):
		# 红色
		return COLOR_MAP['red']

	def green(self):
		# 绿色
		return COLOR_MAP['green']

	def blue(self):
		# 蓝色
		return COLOR_MAP['blue']

	def yellow(self):
		# 黄色
		return COLOR_MAP['yellow']

	def purple(self):
		# 紫色
		return COLOR_MAP['purple']

	def black(self):
		# 黑色
		return COLOR_MAP['black']

	def brown(self):
		# 棕色
		return COLOR_MAP['brown']

	def white(self):
		# 白色
		return COLOR_MAP['white']

	def cyan(self):
		# 青色
		return COLOR_MAP['cyan']

	def getColor(self, color):
		"""
		获取指定色值
		:param color: 颜色
		:return: 色值
		"""
		try:
			return COLOR_MAP[color]
		except KeyError:
			print "Color: Error to get color %s" % color
			return self.black()


class LogColour(Color):
	def __init__(self):
		"""
		彩色打印log
		"""
		self.colorend = '\033[0m'

	def printlog(self, log,	color):
		"""
		打印日志
		:param log: 日志
		:param color: 色值
		:return: None
		"""
		logs = "%s%s%s" % (self.getColor(color), log, self.colorend)
		print logs


# 测试
def doTest():
	lc = LogColour()
	lc.printlog('hello, world', 'red')
	lc.printlog('hello, world', 'green')
	lc.printlog('hello, world', 'blue')
	lc.printlog('hello, world', 'yellow')
	lc.printlog('hello, world', 'purple')
	lc.printlog('hello, world', 'black')
	lc.printlog('hello, world', 'brown')
	lc.printlog('hello, world', 'white')
	lc.printlog('hello, world', 'cyan')
	lc.printlog('hello, world', 'nocolor')

if __name__ == '__main__':
	doTest()
