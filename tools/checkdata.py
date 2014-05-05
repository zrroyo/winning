#! /usr/bin/python
#-*- coding:utf-8 -*-

'''
核对数据表与数据文件中数据是否一致。
'''

import sys
sys.path.append(".")

from date import *
from dataMgr.data import *
from misc.debug import *
from misc.execcmd import *
from misc.dateTime import *

#数据集
class DataUnion:
	def __init__ (self,
		open,
		highest,
		lowest,
		close,
		):
		self.open = open
		self.highest = highest
		self.lowest = lowest
		self.close = close

#核对数据类
class CheckData:
	
	shell = ExecCommand()	#通用命令执行接口
	
	def __init__ (self,
		database,	#数据库
		table,		#数据表
		datfile,	#数据文件
		debug = False,	#是否调试
		):
		self.debug = Debug('CheckData', debug)	#调试接口
		self.data = Data(database, table)
		self.date = Date(database, table)
		self.datfile = datfile
	
	#从数据表中提取记录
	def __dataToDataUnion (self,
		date,	#时间
		):
		self.debug.dbg('Open %s, Highest %s, Lowest %s, Close %s' % 
				(self.data.getOpen(date), self.data.getHighest(date), 
				self.data.getLowest(date), self.data.getClose(date)))
		
		return DataUnion(open = self.data.getOpen(date),
			highest = self.data.getHighest(date),
			lowest = self.data.getLowest(date),
			close = self.data.getClose(date),
			)
	
	#转换时间为数据文件中的格式
	def __convertDateAsFile (self,
		date,	#时间
		):
		dtime = strToDatetime(date, "%Y-%m-%d")
		self.debug.dbg('dtime %s' % dtime)
		return datetimeToStr(dtime, "%m/%d/%Y")
	
	#从数据文件中提取记录
	def __fileToDataUnion (self,
		date,	#时间
		):
		fDate = self.__convertDateAsFile(date)
		fDate = fDate.replace('/', '\/')
		self.debug.dbg('fDate %s' % fDate)
		self.shell.execCmd("sed -n '/%s/p' %s" % (fDate, self.datfile))
		self.debug.dbg(self.shell.getOutput())
		info = self.shell.getOutput().split(',')
		
		return DataUnion(open = float(info[1]),
			highest = float(info[2]),
			lowest = float(info[3]),
			close = float(info[4]),
			)
	
	#比较两个数据集合是否相等
	def __compDataUnion (self,
		du1,
		du2,
		):
		if du1.open == du2.open and du1.highest == du2.highest and du1.lowest == du2.lowest and du1.close == du2.close:
			return True
		else:
			return False
	
	#开始核对
	def startChecking (self,
		days,	#核对天数
		):
		self.debug.dbg('Last Date %s' % self.date.lastDate())
		self.date.setCurDate(self.date.lastDate())
		
		status = True
		while days > 0:
			curDate = self.date.curDate()
			ddu = self.__dataToDataUnion(curDate)
			fdu = self.__fileToDataUnion(curDate)
			if self.__compDataUnion(ddu, fdu):
				self.debug.info('%s: match' % curDate)
			else:
				self.debug.info('%s: dismatch' % curDate)
				status = False
			
			self.date.getSetPrevDate()
			days -= 1
		
		return status
		
##测试
#def doTest ():
	#cd = CheckData('current', 'FG501_dayk', '../tmp/current01/FG501.txt', debug = False)
	#cd.startChecking(15)
	
#入口
if __name__ == '__main__':
	#doTest()
	if len(sys.argv) != 5:
		print '使用: ./checkdata.py current FG501_dayk FG501.txt 15'
		exit(1)
		
	cd = CheckData(sys.argv[1], sys.argv[2], sys.argv[3])
	print cd.startChecking(int(sys.argv[4]))
	