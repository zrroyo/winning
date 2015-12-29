#! /usr/bin/python
#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2014年 03月 19日 星期三 10:55:06 CST

This program is provided under the Gnu General Public License (GPL)
version 2 ONLY.
"""

import sys
from colors import *

#原生Debug类
class RawDebug:

	colourLog = LogColour()	#彩色打输出接口

	def __init__ (self,
		verbose,	#是否打印dbg信息
		destLog = None,	#是否保存日志
		):
		self.verbose = verbose
		self.storeLog = None
		try:
			self.storeLog = open(destLog, "a+")
		except IOError, e:
			print str(e)
		except TypeError, e:
			pass

	def __del__ (self):
		try:
			self.storeLog.close()
		except AttributeError, e:
			pass
	
	#日志换行
	def __wrappedLog (self, 
		log,	#日志
		):
		return log + "\n"
	
	def pr_err (self, 
		str,	#输出
		):
		log = "ERR: %s" % str
		self.colourLog.printlog(log, 'red')
		if self.storeLog:
			self.storeLog.write(self.__wrappedLog(log))
	
	def pr_info (self, 
		str,	#输出
		):
		log = "INFO: %s" % str
		self.colourLog.printlog(log, 'green')
		if self.storeLog:
			self.storeLog.write(self.__wrappedLog(log))
	
	def pr_log (self, 
		str,	#输出
		):
		log = "LOG: %s" % str
		self.colourLog.printlog(log, 'black')
		if self.storeLog:
			self.storeLog.write(self.__wrappedLog(log))
	
	def pr_raw (self, 
		str,	#输出
		):
		log = self.__wrappedLog(str)
		colorLog = self.colourLog.blue() + log + self.colourLog.colorend
		sys.stdout.write(colorLog)
		sys.stdout.flush()
		if self.storeLog:
			self.storeLog.write(log)
	
	def pr_debug (self, 
		str,	#输出
		):
		log = "DBG: %s" % str
		if self.storeLog:
			self.storeLog.write(self.__wrappedLog(log))
		
		if self.verbose:
			#self.colourLog.printlog(log, 'black')
			print log
	
#Debug类
class Debug:
	def __init__ (self,
		prompt,			#打印提示
		verbose = False,	#是否显示debug信息
		):
		self.prompt = prompt
		self.debug = RawDebug(verbose)
		
	#打印错误
	def error (self, 
		msg,	#错误信息
		):
		output = '%s: %s' % (self.prompt, msg)
		self.debug.pr_err(output)
	
	#打印debug信息
	def dbg (self, 
		msg,	#调试信息
		):
		output = '%s: %s' % (self.prompt, msg)
		self.debug.pr_debug(output)
		
	#打印信息
	def warn (self, 
		msg,	#打印信息
		):
		output = '%s: %s' % (self.prompt, msg)
		self.debug.pr_warn(output)
	
	#打印信息
	def info (self, 
		msg,	#打印信息
		):
		output = '%s' % (msg)
		self.debug.pr_info(output)
	
#测试
def doTest ():
	dbg = RawDebug(1)
	dbg.pr_err('Hello world!')
	dbg.pr_info('Hello world!')
	dbg.pr_log('Hello world!')
	dbg.pr_raw('Hello world!')
	dbg.pr_debug('Hello world!')
	
	dbg = Debug('test', 1)
	dbg.error('Test debug error.')
	dbg.dbg('Test debug dbg.')
	
if __name__ == '__main__':
	doTest()
