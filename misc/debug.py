#! /usr/bin/python
#-*- coding:utf-8 -*-

'''
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2014年 03月 19日 星期三 10:55:06 CST

This program is provided under the Gnu General Public License (GPL)
version 2 ONLY.
'''

import sys

#原生Debug类
class RawDebug:
	def __init__ (self,
		verbose,	#是否显示debug信息
		):
		self.verbose = verbose
		
	def pr_err (self, str):
		print "ERR: %s" % str
	
	def pr_info (self, str):
		print "INFO: %s" % str
	
	def pr_log (self, str):
		print "LOG: %s" % str
	
	def pr_warn (self, str):
		print "WARN: %s" % str
	
	def pr_raw (self, str):
		sys.stdout.write(str)
		sys.stdout.flush()
	
	def pr_debug (self, str):
		if self.verbose:
			print "DBG: %s" % str
		
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
	
##测试
#def doTest ():
	#dbg = RawDebug(1)
	#dbg.pr_err('Hello world!')
	#dbg.pr_info('Hello world!')
	#dbg.pr_log('Hello world!')
	#dbg.pr_raw('Hello world!')
	#dbg.pr_debug('Hello world!')
	
	#dbg = Debug('test', 1)
	#dbg.error('Test debug error.')
	#dbg.dbg('Test debug dbg.')
	
#if __name__ == '__main__':
	#doTest()
