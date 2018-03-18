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
from misc.dateTime import *

class Date:
	def __init__ (self, database, table, startTick = None,
			endTick = None, debug = False):
		"""
		交易时间管理接口。从数据库中读取所有交易时间，以加速读取。
		:param database: 数据库
		:param table: 数据表
		:param startTick: 指定开始tick
		:param endTick: 指定结束tick
		:param debug: 是否调试
		"""
		self.debug = Debug('Date', debug)	#调试接口
		self.db = SQL()
		self.db.connect(database)
		self.table = table
		self.startTick = startTick
		self.endTick = endTick
		# 存放ticks的缓冲区
		self.ticksBuffer = []
		self.numTicks = 0
		self.current = 0
		# 交易时间字符格式
		self.dFormat = None
		self.__loadTicks()

	def __del__ (self):
		self.db.close()

	def __loadTicks (self):
		"""
		从数据库中加载所有交易时间
		:return: None
		"""
		# 支持仅加载指定区间的tick
		clause = ""
		if self.startTick:
			clause = "%s >= '%s'" % (F_TIME, self.startTick)

		if self.endTick:
			_clause = "%s <= '%s'" % (F_TIME, self.endTick)
			clause =  "%s and %s" % (clause, _clause) if len(clause) else _clause

		if len(clause):
			clause = "where %s" % clause

		strSql = 'select %s from %s %s order by %s asc' % (
				F_TIME, self.table, clause, F_TIME)
		self.db.execSql(strSql)
		# time = self.db.fetch(all)[FN_TIME]
		self.ticksBuffer = [ e[0] for e in list(self.db.fetch('all'))]
		# self.debug.dbg(self.ticksBuffer)
		self.numTicks = len(self.ticksBuffer)
		self.current = 0
		self.dFormat = TickDetail.tickFormat(self.firstDate())
		# self.debug.dbg("__loadTicks: ticks buffer %s, num %s" % (
		# 		self.ticksBuffer, self.numTicks))

	@staticmethod
	def dateToString (date):
		"""
		把数据库时间转换成字符串
		:param date: 交易时间
		:return: 时间字符串
		"""
		return "%s" % date

	def convertToDBtime (self, date):
		"""
		将传入时间转化为数据库时间
		:param date: 交易时间，且必须为datetime格式。
		:return: 数据库时间
		"""
		# datetime类型要包含时间
		if self.dFormat.find('%H') > 0:
			return date

		return date.date()

	def strToDateTime (self, strDate):
		"""
		把时间字符串转换成数据库时间。
		:param strDate: 时间字符串
		:return: 数据库时间
		"""
		try:
			ret = datetime.strptime(strDate, self.dFormat)
			return self.convertToDBtime(ret)
		except ValueError, e:
			self.debug.warn("strToDateTime: found date doesn't match tick format.")
			ret = strToDatetime(strDate, DB_FORMAT_DATE)
			if not ret:
				ret = strToDatetime(strDate, DB_FORMAT_DATETIME)

			return self.convertToDBtime(ret)

	def curDate (self):
		"""
		返回当前交易时间
		:return: 当前交易时间
		"""
		try:
			return self.ticksBuffer[self.current]
		except IndexError, e:
			self.debug.dbg("curDate: %s" % e)
			return None
	
	def firstDate (self):
		"""
		返回数据表里的第一个交易时间
		:return: 首个交易时间，没有返回None
		"""
		try:
			return self.ticksBuffer[0]
		except IndexError, e:
			self.debug.dbg("firstDate: %s" % e)
			return None
	
	def lastDate (self):
		"""
		返回数据表里的最后一个交易时间
		:return: 最后一个交易时间，没有返回None
		"""
		try:
			return self.ticksBuffer[self.numTicks - 1]
		except IndexError, e:
			self.debug.dbg("firstDate: %s" % e)
			return None

	def isFirstDate (self, date):
		"""
		是否是第一个交易时间
		:param date: 交易时间
		:return: 是返回True，否则返回False
		"""
		if isinstance(date, str):
			date = self.strToDateTime(date)

		return True if date == self.firstDate() else False
	
	def isLastDate (self, date):
		"""
		是否是最后一个交易时间
		:param date: 交易时间
		:return: 是返回True，否则返回False
		"""
		if isinstance(date, str):
			date = self.strToDateTime(date)

		return True if date == self.lastDate() else False
	
	def nextDate (self):
		"""
		返回当前交易时间后的下一个交易时间
		:return: 下一个交易时间，没有返回None
		"""
		try:
			ret = self.ticksBuffer[self.current + 1]
			self.debug.dbg("current %s, ret %s " % (self.current, ret))
			return ret
		except IndexError, e:
			self.debug.dbg("nextDate: %s" % e)
			return None

	def prevDate (self):
		"""
		返回当前交易时间前的上一个交易时间
		:return: 前一个交易时间，没有返回None
		"""
		try:
			return self.ticksBuffer[self.current - 1]
		except IndexError, e:
			self.debug.dbg("prevDate: %s" % e)
			return None

	def setCurDate (self, date):
		"""
		设置当前交易时间
		:param date: 交易时间
		:return: None
		"""
		try:
			if isinstance(date, str):
				date = self.strToDateTime(date)

			idx = self.ticksBuffer.index(date)
			self.current = idx
		except ValueError, e:
			self.debug.error("setCurDate: error: %s" % e)
	
	def getSetNextDate (self):
		"""
		设置下一交易时间为当前交易时间，并返回
		:return: 下一交易时间
		"""
		ret = self.nextDate()
		if ret:
			self.current += 1

		return ret

	def getSetPrevDate (self):
		"""
		设置上一交易时间为当前交易时间，并返回
		:return: 上一交易时间
		"""
		ret = self.prevDate()
		if ret:
			self.current -= 1

		return ret

	def getNexNumDate (self, date, limit):
		"""
		返回指定交易时间之后的第@limit个交易时间
		:param date: 交易时间
		:param limit: 限制数目
		:return: 指定时间之后第limit个交易时间
		"""
		try:
			if isinstance(date, str):
				date = self.strToDateTime(date)

			idx = self.ticksBuffer.index(date)
			idx += limit
			ret =  self.ticksBuffer[idx]
			# self.debug.dbg("getNexNumDate: limit %s, %s" % (limit, ret))
			return ret

		except (ValueError, IndexError), e:
			self.debug.dbg("getNexNumDate: limit %s, error: %s" % (limit, e))
			return None

	def getPrevNumDate (self, date, limit):
		"""
		返回指定交易时间之前的第@limit个交易时间
		:param date: 交易时间
		:param limit: 限制数目
		:return: 指定时间之前第limit个交易时间
		"""
		return self.getNexNumDate(date, -limit)
		
	def getDateIndex (self, date):
		"""
		返回交易时间在数据表中的索引号（位置）
		:param date: 交易时间
		:return: 指定时间索引
		"""
		try:
			if isinstance(date, str):
				date = self.strToDateTime(date)

			return self.ticksBuffer.index(date)
		except ValueError, e:
			self.debug.dbg("getDateIndex: %s" % e)
			return None

	def getNextNearDate (self, date, limit):
		"""
		返回与传入date最近的tick
		:param date: 交易时间
		:param limit: 限制数目
		:return: 指定时间之后下一时间
		"""
		try:
			if isinstance(date, str):
				date = self.strToDateTime(date)

			strSql = "select %s from %s where %s >= '%s' order by %s asc limit %s" % (
					F_TIME, self.table, F_TIME, date, F_TIME, limit)
			self.db.execSql(strSql)
			ret = self.db.fetch(limit - 1)[FN_TIME]
			return ret
		except TypeError, e:
			self.debug.dbg("getNextNearDate: %s" % e)
			return None

	def dayLasts (self, origin, now):
		"""
		交易持续的天数，不包括起始时间点
		:param origin: 起始时间
		:param now: 现在时间
		:return: 交易持续天数
		"""
		strSql = "SELECT COUNT(DISTINCT(DATE_FORMAT(%s, " % F_TIME + \
			"'%Y%m%d'))) AS DAY_LAST " + "FROM %s WHERE %s >= '%s' AND %s <= '%s'" % (
			self.table, F_TIME, origin, F_TIME, now)
		self.db.execSql(strSql)
		ret = self.db.fetch(0)[0] - 1
		return ret


class Ticks(Date):
	def curTick (self):
		"""
		返回当前Tick
		:return: 当前Tick
		"""
		return self.curDate()
	
	def firstTick (self):
		"""
		返回数据表里的第一个Tick
		:return: 第一个Tick
		"""
		return self.firstDate()

	def lastTick (self):
		"""
		返回数据表里的最后一个Tick
		:return: 最后一个Tick
		"""
		return self.lastDate()

	def dayLastTick(self, tick):
		"""
		获取交易日的最后一个tick
		:param tick: 交易时间
		:return: 交易日的最后一个tick
		"""
		try:
			if isinstance(tick, str):
				date = self.strToDateTime(tick)

			strSql = "select %s from %s where date(%s) = '%s' order by %s desc limit 1" % (
					F_TIME, self.table, F_TIME, tick.date(), F_TIME)
			self.db.execSql(strSql)
			ret = self.db.fetch()[0]
			return ret
		except TypeError, e:
			self.debug.dbg("dayLastTick: %s" % e)
			return None

	def isFirstTick (self, tick):
		"""
		是否是第一个交易时间
		:param tick: 交易时间
		:return: 是返回True，否则返回False
		"""
		return self.isFirstDate(tick)
	
	def isLastTick (self, tick):
		"""
		是否是最后一个交易时间
		:param tick: 交易时间
		:return: 是返回True，否则返回False
		"""
		return self.isLastDate(tick)
	
	def nextTick (self):
		"""
		返回当前交易时间后的下一个交易时间
		:return: 下一个交易时间，没有返回None
		"""
		return self.nextDate()
	
	def prevTick (self):
		"""
		返回当前交易时间前的上一个交易时间
		:return: 前一个交易时间，没有返回None
		"""
		return self.prevDate()
	
	def setCurTick (self, tick):
		"""
		设置当前交易时间
		:param tick: 交易时间
		:return: None
		"""
		return self.setCurDate(tick)
	
	def getSetNextTick (self):
		"""
		设置下一交易时间为当前交易时间，并返回
		:return: 下一交易时间
		"""
		return self.getSetNextDate()
	
	def getSetPrevTick (self):
		"""
		设置上一Tick为当前Tick，并返回
		:return: 上一交易时间
		"""
		return self.getSetPrevDate()
	
	def getNexNumTick (self, tick, limit):
		"""
		返回指定交易时间之后的第@limit个交易时间
		:param tick: 交易时间
		:param limit: 限制数目
		:return: 指定时间之后第limit个交易时间
		"""
		return self.getNexNumDate(tick, limit)

	def getPrevNumTick (self, tick, limit):
		"""
		返回指定交易时间之前的第@limit个交易时间
		:param tick: 交易时间
		:param limit: 限制数目
		:return: 指定时间之前第limit个交易时间
		"""
		return self.getPrevNumDate(tick, limit)
	
	def getTickIndex (self, tick):
		"""
		返回交易时间在数据表中的索引号（位置）
		:param tick: 交易时间
		:return: 指定时间索引
		"""
		return self.getDateIndex(tick)

	def getNextNearTick (self, tick, limit):
		"""
		返回与传入date最近的tick
		:param tick: 交易时间
		:param limit: 限制数目
		:return: 指定时间之后下一时间
		"""
		return self.getNextNearDate(tick, limit)

class TickDetail:
	def __init__(self, debug = False):
		"""
		获取Tick细节
		:param debug: 是否调试
		"""
		self.debug = Debug('TickDetail', debug)	#调试接口

	@staticmethod
	def tickFormat (tick):
		"""
		检测tick格式。支持datetime, datetime.date, 以及以
		"%Y-%m-%d %H:%M:%S"或"%Y-%m-%d"格式字符时间。
		:param tick: 交易时间
		:return: 交易时间字符串格式
		"""
		if isinstance(tick, str):
			tickL = tick.split(' ')
			if len(tickL) == 2:
				strFormat = "%Y-%m-%d %H:%M:%S"
			else:
				strFormat = "%Y-%m-%d"
		elif isinstance(tick, datetime):
			strFormat = "%Y-%m-%d %H:%M:%S"
		else:
			strFormat = "%Y-%m-%d"

		return strFormat

#测试
def doTest ():
	tick = Ticks('history2', 'p1601_mink',
			startTick = '2015-01-16 23:37:00',
			endTick = '2015-05-08 11:27:00',
			debug = False)
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
	print tick.isFirstTick("2015-01-16 23:37:00")
	print tick.isLastTick('2015-05-08 11:27:00')
	print tick.isFirstTick('2015-05-09 11:29:00')
	print tick.isLastTick('2015-05-09 11:29:00')
	print tick.getTickIndex(time)
	print tick.getNextNearTick('2015-05-08 11:27:00', 1)
	print tick.getNextNearTick('2015-05-08', 1)

	print TickDetail.tickFormat('2015-05-09 11:29:00')
	print TickDetail.tickFormat('2015-05-09')
	print tick.strToDateTime('2013-12-31 1:31:5')
	# 测试是否能转化成date时间
	tick.dFormat = "%Y-%m-%d"
	ret = tick.strToDateTime('2013-12-31')
	print type(ret), ret

	#测试结果
	'''
	First Tick 2015-01-16 23:37:00
	Last Tick 2015-05-08 11:27:00
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
	13
	2015-05-08 11:27:00
	WARN: Date: strToDateTime: found date doesn't match tick format.
	2015-05-08 00:00:00
	%Y-%m-%d %H:%M:%S
	%Y-%m-%d
	2013-12-31 01:31:05
	<type 'datetime.date'> 2013-12-31
	'''

#
def doTest2 ():
	# tickSrc = Ticks("history", "p1405_dayk", True)
	tickSrc = Ticks('history2', 'p1601_mink', debug = True)


if __name__ == '__main__':
	doTest()
	# doTest2()
