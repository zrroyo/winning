#! /usr/bin/python
#-*- coding:utf-8 -*-

'''
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>

交易时间管理模块
'''

from db.sql import *
from db.tbldesc import *
from misc.debug import *

#交易时间管理接口
class Date:
	
	debug = Debug('Date', False)	#调试接口
	
	def __init__ (self, database, table):
		self.db = SQL()
		self.db.connect(database)
		self.fillDates(table)
		self.table = table
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
		strSql = 'select %s from %s order by %s asc limit 1' % (
				F_TIME, self.table, F_TIME)
		self.db.execSql(strSql)
		time = self.db.fetch(0)[FN_TIME]
		self.debug.dbg("firstDate %s" % time)
		return self.__dateToString(time)
	
	#返回数据表里的最后一个交易时间
	def lastDate (self):
		strSql = "select %s from %s order by %s desc limit 1" % (
				F_TIME, self.table, F_TIME)
		self.db.execSql(strSql)
		time = self.db.fetch(0)[FN_TIME]
		self.debug.dbg("lastDate %s" % time)
		return self.__dateToString(time)
	
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
	
	#返回传入交易时间后的第某个交易时间
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
	
	#返回传入交易时间前的第某个交易时间
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
	
#测试
def doTest ():
	date = Date('history2', 'p1601_mink')
	print "First Date %s" % date.firstDate()
	print "Last Date %s" % date.lastDate()
	time = '2015-01-19 10:56:00'
	date.setCurDate(time)
	print "Current Time %s" % date.curDate()
	print "Prev Date %s" % date.prevDate()
	print "Next Date %s" % date.nextDate()
	date.getSetNextDate()
	print "Current Time %s" % date.curDate()
	date.getSetPrevDate()
	print "Current Time %s" % date.curDate()
	print date.getPrevNumDate(time, 10)
	print date.getNexNumDate(time, 10)
	print date.isFirstDate("2015-01-16 21:00:00")
	print date.isLastDate('2015-05-08 11:29:00')
	print date.isFirstDate('2015-05-09 11:29:00')
	print date.isLastDate('2015-05-09 11:29:00')
	
	#测试结果
	'''
	First Date 2015-01-16 21:00:00
	Last Date 2015-05-08 11:29:00
	Current Time 2015-01-19 10:56:00
	Prev Date 2015-01-19 10:53:00
	Next Date 2015-01-19 11:01:00
	Current Time 2015-01-19 11:01:00
	Current Time 2015-01-19 10:56:00
	2015-01-19 09:08:00
	2015-01-19 13:49:00
	True
	True
	False
	False
	'''

if __name__ == '__main__':
	doTest()
	