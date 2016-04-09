#! /usr/bin/python
#-*- coding:utf-8 -*-

import sys
sys.path.append("..")
import time
import math

from misc.debug import Debug
from db.sql import SQL
from db.tbldesc import *
from core.date import Date
#from ctp.ctpagent import MarketDataAgent

#数据库数据对象
class Data:
	def __init__ (self,
		contract, 	#合约
		config,		#合约配置解析接口
		debug = False,	#是否调试
		):
		self.debug = Debug("Data", debug)	#调试接口
		self.contract = contract
		self.config = config
		self.database = self.config.getDatabase(contract)
		self.table = self.config.getMainTable(contract)
		self.startTick = self.config.getContractStart(contract)
		self.endTick = self.config.getContractEnd(contract)

		self.db = SQL()
		self.db.connect(self.database)
		self.clause = self.__initClause()	#查询条件
		self.current = None	#当前数据（缓冲，优化查询速度）

	def __del__ (self):
		self.db.close()

	# 初始化查询条件
	def __initClause (self):
		# 支持仅加载指定区间的tick
		clause = ""
		if self.startTick:
			clause = "%s >= '%s'" % (F_TIME, self.startTick)

		if self.endTick:
			_clause = "%s <= '%s'" % (F_TIME, self.endTick)
			clause =  "%s and %s" % (clause, _clause) if len(clause) else _clause

		return clause

	# 将时间转化为datetime
	@staticmethod
	def dateConverter (
		date,
		):
		# 支持时间字符串
		if isinstance(date, str):
			date = Date.strToDateTime(date)

		return date

	# 计算移动平均值
	def M (self,
		date,	#时间
		field,	#字段
		days,	#移动时间
		):
		strSql = "select avg(%s) from ( \
			select * from %s where %s and %s <= '%s' order by %s desc limit %s) as T1" % (
				field, self.table, self.clause, F_TIME, date, F_TIME, days)

		self.db.execSql(strSql)

		try:
			ret = self.db.fetch(0)[0]
			# self.debug.dbg("__fetchDataWithinDays: %s" % ret)
			return ret
		except IndexError, e:
			# 严重错误，需及时提醒
			self.debug.error("M: error: %s" % e)
			return None

	# 5日移动平均值
	def M5 (self,
		date,
		field = F_CLOSE,
		):
		return self.M(date, field, 5)
	
	# 10日移动平均值
	def M10 (self,
		date,
		field = F_CLOSE,
		):
		return self.M(date, field, 10)
	
	# 20日移动平均值
	def M20 (self,
		date,
		field = F_CLOSE,
		):
		return self.M(date, field, 20)
	
	# 30日移动平均值
	def M30 (self,
		date,
		field = F_CLOSE,
		):
		return self.M(date, field, 30)
	
	# 60日移动平均值
	def M60 (self,
		date,
		field = F_CLOSE,
		):
		return self.M(date, field, 60)

	# 获得字段值
	def getField (self,
		date,	#交易时间
		field,	#字段
		):
		try:
			# 如果数据已缓存则直接返回
			date = Data.dateConverter(date)
			_fn_ret = DATA_TBL_F_FN_MAP[field]
			_fn_tm = DATA_TBL_F_FN_MAP[F_TIME]
			# self.debug.dbg("_fn_ret %s, _fn_tm %s" % (_fn_ret, _fn_tm))
			if self.current and date == self.current[_fn_tm]:
				return self.current[_fn_ret]

			#数据不在缓冲区中，需查询
			strSql = "select * from %s where %s and %s = '%s'" % (
					self.table, self.clause, F_TIME, date)
			# self.debug.dbg("strSql: %s" % strSql)
			self.db.execSql(strSql)
			self.current = self.db.fetch()
			# self.debug.dbg(self.current)
			return self.current[_fn_ret]

		except KeyError, e:
			# 严重错误，需及时提醒
			self.debug.error("getField: error: %s" % e)
			return None

	# 获得开盘价
	def getOpen (self,
		date,
		):
		return self.getField(date, F_OPEN)

	# 获得收盘价
	def getClose (self,
		date,
		):
		return self.getField(date, F_CLOSE)

	# 获得当日均价
	def getAvg (self,
		date,
		):
		return self.getField(date, F_AVG)

	# 获得最高价
	def getHighest (self,
		date,
		):
		return self.getField(date, F_HIGH)

	# 获得最低价
	def getLowest (self,
		date,
		):
		return self.getField(date, F_LOW)

	# 获得交易时间前N天的最小值
	def lowestWithinDays (self,
		date,
		days,
		field = F_CLOSE,
		exclude = True,		#是否包含传入时间
		):
		sign = '<='
		if exclude:
			sign = '<'
			days -= 1

		strSql = "select min(%s) from ( \
			select * from %s where %s and %s %s '%s' order by %s desc limit %s) as T1" % (
				field, self.table, self.clause, F_TIME, sign, date, F_TIME, days)

		self.db.execSql(strSql)
		ret = self.db.fetch(0)[0]
		return ret

	# 获得交易时间前N天的最大值
	def highestWithinDays (self,
		date,
		days,
		field = F_CLOSE,
		exclude = True,		#是否包含传入时间
		):
		sign = '<='
		if exclude:
			sign = '<'
			days -= 1

		strSql = "select max(%s) from ( \
			select * from %s where %s and %s %s '%s' order by %s desc limit %s) as T1" % (
				field, self.table, self.clause, F_TIME, sign, date, F_TIME, days)

		self.db.execSql(strSql)
		ret = self.db.fetch(0)[0]
		return ret

#CTP数据对象
class CtpData(Data):
	def __init__ (self, 
		instrument, 	#合约号
		database, 	#存储数据库名
		table, 		#数据库中的数据表
		workDay,	#工作日,必须以'%Y-%m-%d'格式
		mdagent		#行情数据代理
		):
		Data.__init__(self, database, table)
		self.instrument = instrument
		self.workDay = workDay
		self.mdlocal = mdagent.mdlocal
		
	#判断是否是已过去的交易日
	def __isPastDate (self, date):
		t1 = time.strptime(date, '%Y-%m-%d')
		t2 = time.strptime(self.workDay, '%Y-%m-%d')
		
		if t1 < t2:
			return True
		elif t1 == t2:
			return False
		else:
			print 'CtpData: Bad date'
			return False
			
	#计算当前交易日的移动均线值
	def ctp_M (self, date, field='Close', days=1):
		'''
		CTP的当前时间必然要大于数据库中所存储的最大时间，
		数据库中存储的为过去的数据，而CTP中的为当前数据。
		'''
		cond = 'Time < "%s" order by Time desc limit %d' % (date, days-1)
		#print cond
		num = self.db.search(self.table, cond, field)
		res = self.db.fetch('all')
		#print res
		#print res[0][0]
		
		if field == 'Close':
			value = self.mdlocal.getClose(self.instrument)
		elif field == 'Open':
			value = self.mdlocal.getOpen(self.instrument)
		elif field == 'Highest':
			value = self.mdlocal.getHighest(self.instrument)
		elif field == 'Lowest':
			value = self.mdlocal.getLowest(self.instrument)
				
		return (self.sum(res) + value) / (num + 1)
		
	#5日移动均线
	def M5 (self, date, field='Close'):
		if self.__isPastDate(date):
			return self.M(date, field, 5)
		else:
			return self.ctp_M(date, field, 5)
			
	#10日移动均线
	def M10 (self, date, field='Close'):
		#print self.__isPastDate(date)
		if self.__isPastDate(date):
			return self.M(date, field, 10)
		else:
			return self.ctp_M(date, field, 10)
	
	#20日移动均线
	def M20 (self, date, field='Close'):
		if self.__isPastDate(date):
			return self.M(date, field, 20)
		else:
			return self.ctp_M(date, field, 20)
			
	#30日移动均线
	def M30 (self, date, field='Close'):
		if self.__isPastDate(date):
			return self.M(date, field, 30)
		else:
			return self.ctp_M(date, field, 30)
			
	#60日移动均线
	def M60 (self, date, field='Close'):
		if self.__isPastDate(date):
			return self.M(date, field, 60)
		else:
			return self.ctp_M(date, field, 60)
			
	#得到开盘价
	def getOpen (self, date):
		if self.__isPastDate(date):
			return self.M(date, 'Open', 1)
		else:
			return self.mdlocal.getOpen(self.instrument)
		
	#得到收盘价
	def getClose (self, date):
		if self.__isPastDate(date):
			return self.M(date, 'Close', 1)
		else:
			return self.mdlocal.getClose(self.instrument)
			
	#得到最高价
	def getHighest (self, date):
		if self.__isPastDate(date):
			return self.M(date, 'Highest', 1)
		else:
			return self.mdlocal.getHighest(self.instrument)
			
	#得到最低价
	def getLowest (self, date):
		if self.__isPastDate(date):
			return self.M(date, 'Lowest', 1)
		else:
			return self.mdlocal.getLowest(self.instrument)
			
	#得到最新更新时间
	def getUpdateTime (self):
		return self.mdlocal.getUpdateTime(self.instrument)

#
def doTest():
	import core.corecfg
	descCfg = core.corecfg.ContractDescConfig('../config/contracts_desc')
	data = Data('p1405', descCfg, False)

	date = '2014-03-11'
	print "Test Middle: Date: %s" % date
	print "M: %s" % data.M(date, F_CLOSE, 1)
	print "M5: %s" % data.M5(date, F_CLOSE)
	print "M10: %s" % data.M10(date, F_CLOSE)
	print "M20: %s" % data.M20(date, F_CLOSE)
	print "M30: %s" % data.M30(date, F_CLOSE)
	print "Open: %s" % data.getOpen(date)
	print "Close: %s" % data.getClose(date)
	print "Avg: %s" % data.getAvg(date)
	print "High: %s" % data.getHighest(date)
	print "Low: %s" % data.getLowest(date)
	print "Highest Before: exclude %s, not exclude %s" % (
		data.highestWithinDays(date, 10, F_CLOSE), data.highestWithinDays(date, 10, F_CLOSE, False))
	print "Lowest Before: exclude %s, not exclude %s" % (
		data.lowestWithinDays(date, 10, F_CLOSE), data.lowestWithinDays(date, 10, F_CLOSE, False))

	date = '2013-05-16'
	print "Test Left Bound: Date: %s" % date
	print "M: %s" % data.M(date, F_CLOSE, 1)
	print "M5: %s" % data.M5(date, F_CLOSE)
	print "M10: %s" % data.M10(date, F_CLOSE)
	print "M20: %s" % data.M20(date, F_CLOSE)
	print "M30: %s" % data.M30(date, F_CLOSE)
	print "Open: %s" % data.getOpen(date)
	print "Close: %s" % data.getClose(date)
	print "Avg: %s" % data.getAvg(date)
	print "High: %s" % data.getHighest(date)
	print "Low: %s" % data.getLowest(date)
	print "Highest Before: exclude %s, not exclude %s" % (
		data.highestWithinDays(date, 10, F_CLOSE), data.highestWithinDays(date, 10, F_CLOSE, False))
	print "Lowest Before: exclude %s, not exclude %s" % (
		data.lowestWithinDays(date, 10, F_CLOSE), data.lowestWithinDays(date, 10, F_CLOSE, False))

	date = '2014-04-30'
	print "Test Right Bound: Date: %s" % date
	print "M: %s" % data.M(date, F_CLOSE, 1)
	print "M5: %s" % data.M5(date, F_CLOSE)
	print "M10: %s" % data.M10(date, F_CLOSE)
	print "M20: %s" % data.M20(date, F_CLOSE)
	print "M30: %s" % data.M30(date, F_CLOSE)
	print "Open: %s" % data.getOpen(date)
	print "Close: %s" % data.getClose(date)
	print "Avg: %s" % data.getAvg(date)
	print "High: %s" % data.getHighest(date)
	print "Low: %s" % data.getLowest(date)
	print "Highest Before: exclude %s, not exclude %s" % (
		data.highestWithinDays(date, 10, F_CLOSE), data.highestWithinDays(date, 10, F_CLOSE, False))
	print "Lowest Before: exclude %s, not exclude %s" % (
		data.lowestWithinDays(date, 10, F_CLOSE), data.lowestWithinDays(date, 10, F_CLOSE, False))

	"""
	Test Middle: Date: 2014-03-11
	M: 6404.0
	M5: 6308.0
	M10: 6222.4
	M20: 6129.9
	M30: 6014.93333333
	Open: 6280.0
	Close: 6404.0
	Avg: 6334.0
	High: 6430.0
	Low: 6230.0
	Highest Before: exclude 6328.0, not exclude 6404.0
	Lowest Before: exclude 6102.0, not exclude 6102.0
	Test Left Bound: Date: 2013-05-16
	M: 6298.0
	M5: 6298.0
	M10: 6298.0
	M20: 6298.0
	M30: 6298.0
	Open: 6246.0
	Close: 6298.0
	Avg: 6274.0
	High: 6326.0
	Low: 6232.0
	Highest Before: exclude None, not exclude 6298.0
	Lowest Before: exclude None, not exclude 6298.0
	Test Right Bound: Date: 2014-04-30
	M: 5876.0
	M5: 5912.0
	M10: 5930.4
	M20: 5963.6
	M30: 6001.73333333
	Open: 5898.0
	Close: 5876.0
	Avg: 5882.0
	High: 5898.0
	Low: 5876.0
	Highest Before: exclude 6002.0, not exclude 6002.0
	Lowest Before: exclude 5900.0, not exclude 5876.0
	"""

if __name__ == '__main__':
	doTest()
