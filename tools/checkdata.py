#! /usr/bin/env python
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
		date,   #时间
		):
		dtime = strToDatetime(date, "%Y-%m-%d")
		#self.debug.dbg('dtime %s' % dtime)
		return datetimeToStr(dtime, "%m/%d/%Y")
	
	#从数据文件中提取记录
	def __fileToDataUnion (self,
		lineNum,	#行号
		):
		self.shell.execCmd("sed -n '%sp' %s" % (lineNum, self.datfile))
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
	
	#得到交易时间所在的行号
	def __dateToLineNum (self,
		date,	#交易时间
		):
		dateTmp = self.__convertDateAsFile(date)
		dateTmp = dateTmp.replace('/', '\/')
		self.shell.execCmd("sed -n '/%s/{=;q}' %s" % (dateTmp, self.datfile))
		lineNum = int(self.shell.getOutput())
		self.debug.dbg('dateTmp %s, lineNum %s' % (dateTmp, lineNum))
		return lineNum
	
	#核对数据表内容
	def checkContent (self,
		days,	#核对天数
		date,	#核对的开始日期
		):
		try:
			self.debug.dbg('Last Date %s' % date)
			self.date.setCurDate(date)
			startLine = self.__dateToLineNum(date)
			
			status = True
			endMatching = False
			while days > 0:
				curDate = self.date.curDate()
				if self.date.isFirstDate(curDate):
					#匹配从表尾向表头进行，匹配到表头结束。
					endMatching = True
				
				ddu = self.__dataToDataUnion(curDate)
				fdu = self.__fileToDataUnion(startLine)
				if self.__compDataUnion(ddu, fdu):
					self.debug.dbg('%s: match' % curDate)
				else:
					self.debug.info('%s: dismatch' % curDate)
					status = False
					
				if endMatching:
					self.debug.info('%s: End of table!' % curDate)
					break
				
				#行号减一，继续上一天
				startLine -= 1
				if startLine == 0:
					self.debug.info('%s: End of file!' % curDate)
					break
				
				self.date.getSetPrevDate()
				days -= 1
			
			return status
		except:
			return False
			
	#核对表头（第一行）
	def checkHead (self,
		date,	#核对的开始日期
		):
		try:
			ddu = self.__dataToDataUnion(date)
			startLine = self.__dateToLineNum(date)
			fdu = self.__fileToDataUnion(startLine)
			if self.__compDataUnion(ddu, fdu):
				self.debug.dbg('%s: head match' % date)
				status = True
			else:
				self.debug.info('%s: head dismatch' % date)
				status = False
		except:
			status = False
		
		return status

##测试
#def doTest ():
	#cd = CheckData('current', 'FG501_dayk', '../tmp/current01/FG501.txt', debug = False)
	#cd.checkContent(15)
	
#入口
if __name__ == '__main__':
	#doTest()
	if len(sys.argv) != 6 and len(sys.argv) != 7:
		print '使用: tools/checkdata.py current FG501_dayk FG501.txt 15 2015-1-28'
		exit(1)
		
	if len(sys.argv) == 6:
		dbgMode = False
	else:
		dbgMode = True
	
	#转换时间格式，确保时间能被date模块正确匹配
	date = datetimeToStr(strToDatetime(sys.argv[5], '%Y-%m-%d'), '%Y-%m-%d')
	
	cd = CheckData(sys.argv[1], sys.argv[2], sys.argv[3], debug = dbgMode)
	print 'Head:    %s' % cd.checkHead(date = date)
	print 'Content: %s' % cd.checkContent(days = int(sys.argv[4]), date = date)
	