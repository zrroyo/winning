#! /usr/bin/env python
#-*- coding:utf-8 -*-

"""
Copyright 2014 Meizu Co., Ltd.
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2014年 03月 20日 星期四 16:05:18 CST

This program is provided under the Gnu General Public License (GPL)
version 2 ONLY.

命令执行模块
	*简化命令执行，并得到最终输出和执行状态。
"""

import os
import commands

#命令执行类
class ExecCommand:
	def __init__ (self):
		self.output = None
		self.status = None
		
	#执行命令
	def execCmd (self, 
		cmdStr,		#命令字符串
		quiet = True,	#是否打印log
		):
		#执行命令	
		if quiet:
			status,output = commands.getstatusoutput(cmdStr)
			self.output = output
			self.status = int(status) / 256
		else:
			status = os.system(cmdStr)
			self.status = int(status) / 256
		
	#返回命令执行结果（输出）
	def getOutput (self):
		return self.output
		
	#返回命令执行状态
	def getStatus (self):
		return self.status
		
	#清除执行状态
	def clear (self):
		self.output = None
		self.status = None
		
##测试		
#def doTest ():
	#ec = ExecCommand()
	#ec.execCmd('ls *')
	#print ec.getOutput()
	#print ec.getStatus()
			
#if __name__ == '__main__':
	#doTest()
		