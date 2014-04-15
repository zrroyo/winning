#! /usr/bin/python
#-*- coding:utf-8 -*-

'''
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
        Wu Zhangjin <wuzhangjin@gmail.com>
Start: 2014年 03月 19日 星期三 10:55:06 CST

This program is provided under the Gnu General Public License (GPL)
version 2 ONLY.
'''

import sys

#Debug类
class Debug:
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
	
	def pr_raw (self, str):
		sys.stdout.write(str)
		sys.stdout.flush()
	
	def pr_debug (self, str):
		if self.verbose:
			print "DBG: %s" % str
		
##测试		
#def doTest ():
	#dbg = Debug(1)
	#dbg.pr_err('Hello world!')
	#dbg.pr_info('Hello world!')
	#dbg.pr_log('Hello world!')
	#dbg.pr_raw('Hello world!')
	#dbg.pr_debug('Hello world!')
			
#if __name__ == '__main__':
	#doTest()
