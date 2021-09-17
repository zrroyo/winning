#! /usr/bin/env python
#-*- coding:utf-8 -*-

'''
Copyright 2014 Meizu Co., Ltd.
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2014年 03月 18日 星期二 16:29:12 CST

This program is provided under the Gnu General Public License (GPL)
version 2 ONLY.
'''

'''
颜色模块：
	*定义普通颜色（值）。
	*定义log输出颜色（值）。
'''

COLOR_MAP = {	'red'	: '\033[0;31m', 
		'green'	: '\033[0;32m',
		'blue'	: '\033[0;34m',
		'yellow': '\033[1;33m',
		'purple': '\033[0;35m',
		'black'	: '\033[0;30m',
		'brown'	: '\033[0;33m',
		'white'	: '\033[1;37m',
		'cyan'	: '\033[0;36m',
		}

#颜色类
class Color:
	#红色
	def red (self):
		return COLOR_MAP['red']
	
	#绿色
	def green (self):
		return COLOR_MAP['green']
	
	#蓝色
	def blue (self):
		return COLOR_MAP['blue']
	
	#黄色
	def yellow (self):
		return COLOR_MAP['yellow']
	
	#紫色
	def purple (self):
		return COLOR_MAP['purple']
	
	#黑色
	def black (self):
		return COLOR_MAP['black']
	
	#棕色
	def brown (self):
		return COLOR_MAP['brown']
	
	#白色
	def white (self):
		return COLOR_MAP['white']
	
	#青色
	def cyan (self):
		return COLOR_MAP['cyan']
	
	#获取指定色
	def getColor (self,
		color,	#颜色
		):
		try:
			return COLOR_MAP[color]
		except:
			print "Color: Error to get color %s" % color
			return self.black()
	
#彩色打印log
class LogColour(Color):
	def __init__ (self):
		self.colorend = '\033[0m'
	
	#打印日志
	def printlog (self,
		log,	#日志
		color,
		):
		logs = "%s%s%s" % (self.getColor(color), log, self.colorend)
		print logs

#测试
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
	