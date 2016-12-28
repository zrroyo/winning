#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2014年 03月 19日 星期三 10:55:06 CST

This program is provided under the Gnu General Public License (GPL)
version 2 ONLY.
"""

import sys
from colors import *

class RawDebug:

	colourLog = LogColour()	#彩色打输出接口

	def __init__ (self, verbose, destLog = None):
		"""
		Debug打印控制
		:param verbose: 是否打印dbg信息
		:param destLog: 是否保存日志
		:return: None
		"""
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
	
	def __wrappedLog (self, log):
		"""
		日志换行
		:param log: 日志
		:return:
		"""
		return log + "\n"
	
	def pr_err (self, msg):
		"""
		打印错误错误
		:param msg: 打印信息
		:return: None
		"""
		log = "ERR: %s" % msg
		self.colourLog.printlog(log, 'red')
		if self.storeLog:
			self.storeLog.write(self.__wrappedLog(log))
	
	def pr_info (self, msg):
		"""
		打印提示信息
		:param msg: 打印信息
		:return: None
		"""
		log = "INFO: %s" % msg
		self.colourLog.printlog(log, 'green')
		if self.storeLog:
			self.storeLog.write(self.__wrappedLog(log))

	def pr_warn (self, msg):
		"""
		打印警告信息
		:param msg: 打印信息
		:return: None
		"""
		log = "WARN: %s" % msg
		self.colourLog.printlog(log, 'brown')
		if self.storeLog:
			self.storeLog.write(self.__wrappedLog(log))

	def pr_log (self, msg):
		"""
		打印日志
		:param msg: 打印信息
		:return: None
		"""
		log = "LOG: %s" % msg
		self.colourLog.printlog(log, 'black')
		if self.storeLog:
			self.storeLog.write(self.__wrappedLog(log))

	def pr_raw (self, msg):
		"""
		打印
		:param msg: 打印信息
		:return: None
		"""
		log = self.__wrappedLog(msg)
		colorLog = self.colourLog.blue() + log + self.colourLog.colorend
		sys.stdout.write(colorLog)
		sys.stdout.flush()
		if self.storeLog:
			self.storeLog.write(log)

	def pr_debug (self, msg):
		"""
		打印debug信息
		:param msg: 打印信息
		:return: None
		"""
		log = "DBG: %s" % msg
		if self.storeLog:
			self.storeLog.write(self.__wrappedLog(log))
		
		if self.verbose:
			#self.colourLog.printlog(log, 'black')
			print log
	
class Debug:
	def __init__ (self, prompt, verbose = False):
		"""
		Debug支持
		:param prompt: 打印提示
		:param verbose: 是否显示debug信息
		:return: None
		"""
		self.verbose = verbose
		self.prompt = prompt
		self.debug = RawDebug(verbose)
		
	def error (self, msg):
		"""
		打印错误错误
		:param msg: 打印信息
		:return: None
		"""
		output = '%s: %s' % (self.prompt, msg)
		self.debug.pr_err(output)
	
	def dbg (self, msg):
		"""
		打印debug信息
		:param msg: 打印信息
		:return: None
		"""
		# 大型数据结构转化为字符串严重影响性能
		if not self.verbose:
			return None
		output = '%s: %s' % (self.prompt, msg)
		self.debug.pr_debug(output)
		
	def warn (self, msg):
		"""
		打印警告信息
		:param msg: 打印信息
		:return: None
		"""
		output = '%s: %s' % (self.prompt, msg)
		self.debug.pr_warn(output)
	
	def info (self, msg):
		"""
		打印提示信息
		:param msg: 打印信息
		:return: None
		"""
		output = '%s: %s' % (self.prompt, msg)
		self.debug.pr_info(output)
	
#测试
def doTest ():
	dbg = RawDebug(1)
	dbg.pr_err('Hello world!')
	dbg.pr_info('Hello world!')
	dbg.pr_debug('Hello world!')
	dbg.pr_warn('Hello world!')
	dbg.pr_log('Hello world!')
	dbg.pr_raw('Hello world!')

	dbg = Debug('test', 1)
	dbg.error('Test debug error.')
	dbg.info('Test debug dbg.')
	dbg.dbg('Test debug dbg.')
	dbg.warn('Test debug dbg.')

if __name__ == '__main__':
	doTest()
