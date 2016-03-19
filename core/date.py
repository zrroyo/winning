#! /usr/bin/python
#-*- coding:utf-8 -*-

'''
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>

交易时间管理模块
'''

import sys
sys.path.append('..')

from db.sql import *
from db.tbldesc import *
from misc.debug import *

#交易时间管理接口
class Date:
	def __init__ (self, 
		database, 	#数据库
		table,		#数据表
		debug = False,	#是否调试
		):
		self.db = SQL()
		self.db.connect(database)
		self.fillDates(table)
		self.table = table
		self.debug = Debug('Date', debug)	#调试接口
		self.__firstDate = None	#第一个tick
		self.__lastDate = None	#最后一个tick
		self.current = self.firstDate()
	
	def __del__ (self):
		self.db.close()
	
	#无意义，仅用于往后兼容性支持
	def fillDates (self, 
		table,
		):
		return
	
	#把数据库时间转换成字符串
	def __dateToString (self, 
		date,	#数据库时间
		):
		return '%s' % date
	
	#返回当前交易时间
	def curDate (self):
		return self.current
	
	#返回数据表里的第一个交易时间
	def firstDate (self):
		if self.__firstDate is not None:
			return self.__firstDate
		
		strSql = 'select %s from %s order by %s asc limit 1' % (
				F_TIME, self.table, F_TIME)
		self.db.execSql(strSql)
		time = self.db.fetch(0)[FN_TIME]
		self.debug.dbg("firstDate %s" % time)
		self.__firstDate = self.__dateToString(time)
		return self.__firstDate
	
	#返回数据表里的最后一个交易时间
	def lastDate (self):
		if self.__lastDate is not None:
			return self.__lastDate
		
		strSql = "select %s from %s order by %s desc limit 1" % (
				F_TIME, self.table, F_TIME)
		self.db.execSql(strSql)
		time = self.db.fetch(0)[FN_TIME]
		self.debug.dbg("lastDate %s" % time)
		self.__lastDate = self.__dateToString(time)
		return self.__lastDate
	
	#是否是第一个交易时间
	def isFirstDate (self, 
		date,	#交易时间
		):
		return True if date == self.firstDate() else False
	
	#是否是最后一个交易时间
	def isLastDate (self, 
		date,	#交易时间
		):
		return True if date == self.lastDate() else False
	
	#返回当前交易时间后的下一个交易时间
	def nextDate (self):
		return self.getNexNumDate(self.current, 1)
	
	#返回当前交易时间前的上一个交易时间
	def prevDate (self):
		return self.getPrevNumDate(self.current, 1)
	
	#设置当前交易时间
	def setCurDate (self, 
		date,	#交易时间
		):
		#不做检验真的好吗？？
		self.current = date
	
	#设置下一交易时间为当前交易时间，并返回
	def getSetNextDate (self):
		self.current = self.nextDate()
		return self.current
	
	#设置上一交易时间为当前交易时间，并返回
	def getSetPrevDate (self):
		self.current = self.prevDate()
		return self.current
	
	#检验交易时间是否有效
	def __validDate (self,
		date,	#交易时间
		):
		if date is None:
			return False
		else:
			return True
	
	#返回传入交易时间后的第@limit个交易时间
	def getNexNumDate (self, 
		date,	#交易时间
		limit,	#限制数目
		):
		strSql = "select %s from %s where %s > '%s' order by %s asc limit %s" % (
				F_TIME, self.table, F_TIME, date, F_TIME, limit)
		self.db.execSql(strSql)
		res = self.db.fetch('all')
		
		#只有返回数量够数才表明查找成功
		if len(res) == limit:
			time = res[limit-1][FN_TIME]
		else:
			time = None
		
		self.debug.dbg("getNexNumDate %s" % time)
		
		if self.__validDate(time):
			return self.__dateToString(time)
		else:
			return None
	
	#返回传入交易时间前的第@limit个交易时间
	def getPrevNumDate (self, 
		date,	#交易时间
		limit,	#限制数目
		):
		strSql = "select %s from %s where %s < '%s' order by %s desc limit %s" % (
				F_TIME, self.table, F_TIME, date, F_TIME, limit)
		self.db.execSql(strSql)
		res = self.db.fetch('all')
		
		#只有返回数量够数才表明查找成功
		if len(res) == limit:
			time = res[limit-1][FN_TIME]
		else:
			time = None
		
		self.debug.dbg("getPrevNumDate %s" % time)
		
		if self.__validDate(time):
			return self.__dateToString(time)
		else:
			return None
		
	#返回交易时间在数据表中的索引号（位置）
	def getDateIndex (self, 
		date,	#交易时间
		):
		strSql = "select count(%s) from %s where %s <= '%s' order by %s desc" % (
				F_TIME, self.table, F_TIME, date, F_TIME)
		self.debug.dbg("getDateIndex strSql: %s" % strSql)
		self.db.execSql(strSql)
		res = self.db.fetch(0)
		return res[0]
	
#Tick(交易时间)管理接口
class Ticks(Date):
	#返回当前Tick
	def curTick (self):
		return self.curDate()
	
	#返回数据表里的第一个Tick
	def firstTick (self):
		return self.firstDate()

	#返回数据表里的最后一个Tick
	def lastTick (self):
		return self.lastDate()
	
	#是否是第一个Tick
	def isFirstTick (self, 
		tick,	#Tick
		):
		return self.isFirstDate(tick)
	
	#是否是最后一个Tick
	def isLastTick (self, 
		tick,	#Tick
		):
		return self.isLastDate(tick)
	
	#返回当前Tick后的下一个Tick
	def nextTick (self):
		return self.nextDate()
	
	#返回当前Tick前的上一个Tick
	def prevTick (self):
		return self.prevDate()
	
	#设置当前Tick
	def setCurTick (self, 
		tick,	#Tick
		):
		return self.setCurDate(tick)
	
	#设置下一Tick为当前Tick，并返回
	def getSetNextTick (self):
		return self.getSetNextDate()
	
	#设置上一Tick为当前Tick，并返回
	def getSetPrevTick (self):
		return self.getSetPrevDate()
	
	#返回传入Tick后的第@limit个Tick
	def getNexNumTick (self, 
		tick,	#Tick
		limit,	#限制数目
		):
		return self.getNexNumDate(tick, limit)

	#返回传入Tick前的第@limit个Tick
	def getPrevNumTick (self, 
		tick,	#Tick
		limit,	#限制数目
		):
		return self.getPrevNumDate(tick, limit)
	
	#返回交易时间在数据表中的索引号（位置）
	def getTickIndex (self, 
		tick,	#交易时间
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
	16
	%Y-%m-%d %H-%M-%S
	%Y-%m-%d
	'''

if __name__ == '__main__':
	doTest()
	