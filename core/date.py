#! /usr/bin/python
#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>

交易时间管理模块
"""

import sys
sys.path.append('..')
from datetime import datetime

from db.sql import *
from db.tbldesc import *
from misc.debug import *

# 交易时间管理接口
class Date:
	def __init__ (self, 
		database, 	#数据库
		table,		#数据表
		debug = False,	#是否调试
		):
		self.debug = Debug('Date', debug)	#调试接口
		self.db = SQL()
		self.db.connect(database)
		self.table = table
		# 存放ticks的缓冲区
		self.ticksBuffer = []
		self.numTicks = 0
		self.current = 0
		self.__loadTicks()

	def __del__ (self):
		self.db.close()

	# 从数据库中加载时间
	def __loadTicks (self):
		strSql = 'select %s from %s order by %s asc' % (
				F_TIME, self.table, F_TIME)
		self.db.execSql(strSql)
		# time = self.db.fetch(all)[FN_TIME]
		self.ticksBuffer = [ e[0] for e in list(self.db.fetch('all'))]
		# self.debug.dbg(self.ticksBuffer)
		self.numTicks = len(self.ticksBuffer)
		self.current = 0
		# self.debug.dbg("__loadTicks: ticks buffer %s, num %s" % (
		# 		self.ticksBuffer, self.numTicks))

	#无意义，仅用于往后兼容性支持
	def fillDates (self, 
		table,
		):
		pass

	# 把数据库时间转换成字符串
	def dateToString (self,
		date,	#数据库时间
		):
		return "%s" % date

	# 把时间字符串转换成数据库时间
	def strToDateTime (self,
		strDate,
		):
		try:
			return datetime.strptime(strDate, "%Y-%m-%d %H:%M:%S")
		except ValueError, e:
			return datetime.strptime(strDate, "%Y-%m-%d").date()

	#返回当前交易时间
	def curDate (self):
		try:
			return self.ticksBuffer[self.current]
		except IndexError, e:
			self.debug.error("curDate: error: %s" % e)
			return None
	
	# 返回数据表里的第一个交易时间
	def firstDate (self):
		try:
			return self.ticksBuffer[0]
		except IndexError, e:
			self.debug.error("firstDate: error: %s" % e)
			return None
	
	# 返回数据表里的最后一个交易时间
	def lastDate (self):
		try:
			return self.ticksBuffer[self.numTicks - 1]
		except IndexError, e:
			self.debug.error("firstDate: error: %s" % e)
			return None

	# 是否是第一个交易时间
	def isFirstDate (self, 
		date,	#交易时间
		):
		if isinstance(date, str):
			date = self.strToDateTime(date)

		return True if date == self.firstDate() else False
	
	# 是否是最后一个交易时间
	def isLastDate (self, 
		date,	#交易时间
		):
		if isinstance(date, str):
			date = self.strToDateTime(date)

		return True if date == self.lastDate() else False
	
	# 返回当前交易时间后的下一个交易时间
	def nextDate (self):
		try:
			ret = self.ticksBuffer[self.current + 1]
			self.debug.dbg("current %s, ret %s " % (self.current, ret))
			return ret
		except IndexError, e:
			self.debug.error("nextDate: error: %s" % e)
			return None

	# 返回当前交易时间前的上一个交易时间
	def prevDate (self):
		try:
			return self.ticksBuffer[self.current - 1]
		except IndexError, e:
			self.debug.error("prevDate: error: %s" % e)
			return None

	# 设置当前交易时间
	def setCurDate (self, 
		date,	#交易时间
		):
		try:
			if isinstance(date, str):
				date = self.strToDateTime(date)

			idx = self.ticksBuffer.index(date)
			self.current = idx
		except ValueError, e:
			self.debug.error("setCurDate: error: %s" % e)
	
	# 设置下一交易时间为当前交易时间，并返回
	def getSetNextDate (self):
		ret = self.nextDate()
		if ret:
			self.current += 1

		return ret

	# 设置上一交易时间为当前交易时间，并返回
	def getSetPrevDate (self):
		ret = self.prevDate()
		if ret:
			self.current -= 1

		return ret

	# 返回指定交易时间之后的第@limit个交易时间
	def getNexNumDate (self, 
		date,	#交易时间
		limit,	#限制数目
		):
		try:
			if isinstance(date, str):
				date = self.strToDateTime(date)

			idx = self.ticksBuffer.index(date)
			idx += limit
			ret =  self.ticksBuffer[idx]
			# self.debug.dbg("getNexNumDate: limit %s, %s" % (limit, ret))
			return ret

		except (ValueError, IndexError), e:
			self.debug.error("getNexNumDate: limit %s, error: %s" % (limit, e))
			return None

	# 返回指定交易时间之前的第@limit个交易时间
	def getPrevNumDate (self, 
		date,	#交易时间
		limit,	#限制数目
		):
		return self.getNexNumDate(date, -limit)
		
	# 返回交易时间在数据表中的索引号（位置）
	def getDateIndex (self, 
		date,	#交易时间
		):
		try:
			if isinstance(date, str):
				date = self.strToDateTime(date)

			return self.ticksBuffer.index(date)
		except ValueError, e:
			self.debug.error("getDateIndex: error: %s" % e)
			return None

# Tick(交易时间)管理接口
class Ticks(Date):
	# 返回当前Tick
	def curTick (self):
		return self.curDate()
	
	# 返回数据表里的第一个Tick
	def firstTick (self):
		return self.firstDate()

	# 返回数据表里的最后一个Tick
	def lastTick (self):
		return self.lastDate()
	
	# 是否是第一个Tick
	def isFirstTick (self, 
		tick,
		):
		return self.isFirstDate(tick)
	
	# 是否是最后一个Tick
	def isLastTick (self, 
		tick,
		):
		return self.isLastDate(tick)
	
	# 返回当前Tick后的下一个Tick
	def nextTick (self):
		return self.nextDate()
	
	# 返回当前Tick前的上一个Tick
	def prevTick (self):
		return self.prevDate()
	
	# 设置当前Tick
	def setCurTick (self, 
		tick,
		):
		return self.setCurDate(tick)
	
	# 设置下一Tick为当前Tick，并返回
	def getSetNextTick (self):
		return self.getSetNextDate()
	
	# 设置上一Tick为当前Tick，并返回
	def getSetPrevTick (self):
		return self.getSetPrevDate()
	
	# 返回传入Tick后的第@limit个Tick
	def getNexNumTick (self, 
		tick,	#Tick
		limit,	#限制数目
		):
		return self.getNexNumDate(tick, limit)

	# 返回传入Tick前的第@limit个Tick
	def getPrevNumTick (self, 
		tick,	#Tick
		limit,	#限制数目
		):
		return self.getPrevNumDate(tick, limit)
	
	# 返回交易时间在数据表中的索引号（位置）
	def getTickIndex (self, 
		tick,
		):
		return self.getDateIndex(tick)

# 获取Tick细节类
class TickDetail:
	def __init__(self,
		debug = False,	#是否调试
		):
		self.debug = Debug('TickDetail', debug)	#调试接口

	# 检测tick格式
	@staticmethod
	def tickFormat (
		tick,	#
		):
		tickL = tick.split(' ')
		if len(tickL) == 2:
			strFormat = "%Y:%m:%d %H:%M:%S"
		else:
			strFormat = "%Y:%m:%d"

		if tick.find('-') != -1:
			sep = '-'

		strFormat = strFormat.replace(':', sep,)
		return strFormat

#测试
def doTest ():
	tick = Ticks('history2', 'p1601_mink', debug = False)
	print "First Tick %s" % tick.firstTick()
	print "Last Tick %s" % tick.lastTick()
	time = '2015-01-19 10:56:00'
	tick.setCurTick(time)
	print "Current Time %s" % tick.curTick()
	print "Prev Tick %s" % tick.prevTick()
	print "Next Tick %s" % tick.nextTick()
	tick.getSetNextTick()
	print "Current Time %s" % tick.curTick()
	tick.getSetPrevTick()
	print "Current Time %s" % tick.curTick()
	print tick.getPrevNumTick(time, 10)
	print tick.getNexNumTick(time, 10)
	print tick.isFirstTick("2015-01-16 21:00:00")
	print tick.isLastTick('2015-05-08 11:29:00')
	print tick.isFirstTick('2015-05-09 11:29:00')
	print tick.isLastTick('2015-05-09 11:29:00')
	print tick.getTickIndex(time)

	print TickDetail.tickFormat('2015-05-09 11:29:00')
	print TickDetail.tickFormat('2015-05-09')

	#测试结果
	'''
	First Tick 2015-01-16 21:00:00
	Last Tick 2015-05-08 11:29:00
	Current Time 2015-01-19 10:56:00
	Prev Tick 2015-01-19 10:53:00
	Next Tick 2015-01-19 11:01:00
	Current Time 2015-01-19 11:01:00
	Current Time 2015-01-19 10:56:00
	2015-01-19 09:08:00
	2015-01-19 13:49:00
	True
	True
	False
	False
	15
	%Y-%m-%d %H-%M-%S
	%Y-%m-%d
	'''

#
def doTest2 ():
	# tickSrc = Ticks("history", "p1405_dayk", True)
	tickSrc = Ticks('history2', 'p1601_mink', debug = True)


if __name__ == '__main__':
	doTest()
	# doTest2()
