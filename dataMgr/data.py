# -*- coding:utf-8 -*-

"""
交易数据
"""

import sys
sys.path.append("..")
import time
import math
import pandas as pd
import numpy as np

from misc.debug import Debug
from misc.dateTime import *
from db.sql import SQL
from db.tbldesc import *
#from ctp.ctpagent import MarketDataAgent


class Data:
	def __init__ (self, contract, config, debug = False):
		"""
		交易数据接口
		:param contract: 合约
		:param config: 合约配置解析接口
		:param debug: 是否调试
		"""
		self.debug = Debug("Data", debug)	#调试接口
		self.contract = contract
		self.config = config
		self.database = self.config.getDatabase(contract)
		self.tableDayk = self.config.getDaykTable(contract)
		self.startTick = self.config.getContractStart(contract)
		self.endTick = self.config.getContractEnd(contract)

		# 数据库接口
		self.db = SQL()
		self.db.connect(self.database)
		# 日K线数据
		self.datDayk = None
		# 根据邻近性原则建立tick数据缓存区
		self.__daykCache = {}
		self.__loadData()

	def __del__ (self):
		self.db.close()

	def __loadData(self):
		"""
		从数据库中导入数据
		:return: None
		"""
		# 读取日k线数据
		strSql = "select * from %s where %s >= '%s' and %s <= '%s'" % (
			self.tableDayk, F_TIME, self.startTick, F_TIME, self.endTick)
		self.datDayk = pd.read_sql(strSql, self.db.conn, index_col = F_TIME)
		# 将index转化为datetime类型
		self.datDayk.index = pd.to_datetime(self.datDayk.index)

	@staticmethod
	def dateConverter (date):
		"""
		将字符格式时间转化为数据表格式时间
		:param date: 字符时间
		:return: 数据表格式时间
		"""
		if not isinstance(date, str):
			return date

		# 支持时间字符串
		ret = strToDatetime(date, DB_FORMAT_DATE)
		if not ret:
			ret = strToDatetime(date, DB_FORMAT_DATETIME)

		return ret

	def M(self, date, field, days):
		"""
		返回指定天数的移动平均值
		:param date: 交易时间
		:param field: 字段
		:param days: 移动单位数
		:return: 移动平均值
		"""
		_date = "%s" % date
		try:
			return self.__daykCache[_date]['M'][field][days]
		except KeyError:
			# @num对应的sum值还没有
			_tmp = self.datDayk[self.datDayk.index <= _date ].tail(days)
			mean = _tmp[field].describe()['mean']

			if _date not in self.__daykCache.keys():
				# tick日期发生变化，依据邻近原则更新缓存区
				self.debug.dbg("M: __daykCache: %s" % self.__daykCache)
				self.__daykCache.clear()
				self.__daykCache[_date] = {}
				self.__daykCache[_date]['M'] = {}
				self.__daykCache[_date]['M'][field] = {}
			elif 'M' not in self.__daykCache[_date].keys():
				self.__daykCache[_date]['M'] = {}
				self.__daykCache[_date]['M'][field] = {}
			elif field not in self.__daykCache[_date]['M'].keys():
				self.__daykCache[_date]['M'][field] = {}

			self.__daykCache[_date]['M'][field][days] = mean
			return mean

	def M5(self, date, field = F_CLOSE):
		"""
		5日移动平均值
		:param date: 交易时间
		:param field: 字段
		:return: 移动平均值
		"""
		return self.M(date, field, 5)
	
	def M10(self, date, field = F_CLOSE):
		"""
		10日移动平均值
		:param date: 交易时间
		:param field: 字段
		:return: 移动平均值
		"""
		return self.M(date, field, 10)
	
	def M20(self, date, field = F_CLOSE):
		"""
		20日移动平均值
		:param date: 交易时间
		:param field: 字段
		:return: 移动平均值
		"""
		return self.M(date, field, 20)
	
	def M30(self, date, field = F_CLOSE):
		"""
		30日移动平均值
		:param date: 交易时间
		:param field: 字段
		:return: 移动平均值
		"""
		return self.M(date, field, 30)
	
	def M60(self, date, field = F_CLOSE):
		"""
		60日移动平均值
		:param date: 交易时间
		:param field: 字段
		:return: 移动平均值
		"""
		return self.M(date, field, 60)

	def getField (self, date, field):
		"""
		获取指定交易时间指定字段值
		:param date: 交易时间
		:param field: 字段
		:return: 没有返回None，有则返回值
		"""
		try:
			date = Data.dateConverter(date)
			return self.datDayk.xs(date)[field]
		except KeyError, e:
			self.debug.dbg("getField: found error: %s" % e)
			return None

	def getOpen(self, date):
		"""
		获取指定交易时间开盘价
		:param date: 交易时间
		:return: 没有返回None，有则返回值
		"""
		return self.getField(date, F_OPEN)

	def getClose(self, date):
		"""
		获取指定交易时间收盘价
		:param date: 交易时间
		:return: 没有返回None，有则返回值
		"""
		return self.getField(date, F_CLOSE)

	def getAvg(self, date):
		"""
		获取指定交易时间平均价
		:param date: 交易时间
		:return: 没有返回None，有则返回值
		"""
		return self.getField(date, F_AVG)

	def getHighest(self, date):
		"""
		获取指定交易时间最高价
		:param date: 交易时间
		:return: 没有返回None，有则返回值
		"""
		return self.getField(date, F_HIGH)

	def getLowest(self, date):
		"""
		获取指定交易时间最低价
		:param date: 交易时间
		:return: 没有返回None，有则返回值
		"""
		return self.getField(date, F_LOW)

	def lowestWithinDays (self, date, days, field = F_CLOSE, exclude = True):
		"""
		获得交易时间前@days天中最小值
		:param date: 交易时间
		:param days: 天数
		:param field: 字段
		:param exclude: 传入tick是否计入
		:return: 几天内最低值
		"""
		_date = "%s" % date
		if exclude:
			ret = self.datDayk[self.datDayk.index < _date].tail(days - 1)[field].min()
		else:
			ret =  self.datDayk[self.datDayk.index <= _date].tail(days)[field].min()

		if ret is np.nan:
			return None
		return ret

	def highestWithinDays (self, date, days, field = F_CLOSE, exclude = True):
		"""
		获得交易时间前@days天中最大值
		:param date: 交易时间
		:param days: 天数
		:param field: 字段
		:param exclude: 传入tick是否计入
		:return: 几天内最低值
		"""
		_date = "%s" % date
		if exclude:
			ret = self.datDayk[self.datDayk.index < _date].tail(days - 1)[field].max()
		else:
			ret = self.datDayk[self.datDayk.index <= _date].tail(days)[field].max()

		if ret is np.nan:
			return None
		return ret

class DataMink(Data):
	def __init__(self, contract, config, debug = False):
		"""
		分钟级交易数据接口
		:param contract: 合约
		:param config: 合约配置解析接口
		:param debug: 是否调试
		"""
		Data.__init__(self, contract, config, debug)
		self.debug = Debug("DataMink", debug)	#调试接口
		self.tableMink = self.config.getMinkTable(contract)

		# 分钟级K线数据
		self.datMink = None
		# 根据邻近性原则建立tick数据缓存区，以加速查询。
		# 如：{'2014-03-11': {
		# 	'lowest': {'Close': {10: 6102.0}},
		# 	'highest': {'Close': {10: 6328.0}},
		# 	'M': {'Close': {1: (0.0, 0), 10: (55820.0, 9),
		# 			20: (116194.0, 19), 5: (25136.0, 4),
		# 			30: (174044.0, 29)}}}}
		self.__minkCache = {}
		self.__loadData()

	def __loadData(self):
		"""
		从数据库中导入数据
		:return: None
		"""
		# 读取分钟级k线数据
		strSql = "select * from %s where %s >= '%s' and %s <= '%s'" % (
			self.tableMink, F_TIME, self.startTick, F_TIME, self.endTick)
		self.datMink = pd.read_sql(strSql, self.db.conn, index_col = F_TIME)
		# 将index转化为datetime类型
		self.datMink.index = pd.to_datetime(self.datMink.index)

	def M(self, tick, field, num):
		"""
		返回指定天数的移动平均值
		:param tick: 交易时间，必须为datetime类型
		:param field: 字段
		:param num: 移动单位数
		:return: 移动平均值
		"""
		_date = "%s" % tick.date()
		try:
			(_sum, _len) = self.__minkCache[_date]['M'][field][num]
			ret = (_sum + self.getField(tick, field)) / (_len + 1)
			return ret
		except KeyError:
			# @num对应的sum值还没有
			# self.debug.dbg("M: _date %s" % _date)
			# self.debug.dbg("M: datDayk.index < %s: %s" % (_date, self.datDayk.index < _date))
			_tmp = self.datDayk[self.datDayk.index < _date ].tail(num - 1)
			_len = len(_tmp)
			_sum = _tmp.sum()[field]

			if _date not in self.__minkCache.keys():
				# tick日期发生变化，依据邻近原则更新缓存区
				self.debug.dbg("M: __minkCache: %s" % self.__minkCache)
				self.__minkCache.clear()
				self.__minkCache[_date] = {}
				self.__minkCache[_date]['M'] = {}
				self.__minkCache[_date]['M'][field] = {}
			elif 'M' not in self.__minkCache[_date].keys():
				self.__minkCache[_date]['M'] = {}
				self.__minkCache[_date]['M'][field] = {}
			elif field not in self.__minkCache[_date]['M'].keys():
				self.__minkCache[_date]['M'][field] = {}

			self.__minkCache[_date]['M'][field][num] = (_sum, _len)

			ret = (_sum + self.getField(tick, field)) / (_len + 1)
			return ret

	def getField(self, tick, field):
		"""
		获取指定交易时间指定字段值
		:param tick: 交易时间
		:param field: 字段
		:return: 没有返回None，有则返回值
		"""
		try:
			return self.datMink.xs(tick)[field]
		except KeyError:
			return None

	def lowestWithinDays (self, tick, days, field = F_CLOSE, exclude = True):
		"""
		获得交易时间前@days天中最小值
		:param tick: 交易时间
		:param days: 天数
		:param field: 字段
		:param exclude: 传入tick是否计入
		:return: 几天内最低值
		"""
		_date = "%s" % tick.date()
		try:
			_vPrior = self.__minkCache[_date]['lowest'][field][days]
			if not exclude:
				# 计入传入tick数据
				_vCur = self.getField(tick, field)
				if _vPrior is None:
					return _vCur
				return min(_vPrior, _vCur)

			return _vPrior
		except KeyError:
			if _date not in self.__minkCache.keys():
				# tick日期发生变化，依据邻近原则更新缓存区
				self.debug.dbg("lowestWithinDays: __minkCache: %s" % self.__minkCache)
				self.__minkCache.clear()
				self.__minkCache[_date] = {}
				self.__minkCache[_date]['lowest'] = {}
				self.__minkCache[_date]['lowest'][field] = {}
			elif 'lowest' not in self.__minkCache[_date].keys():
				self.__minkCache[_date]['lowest'] = {}
				self.__minkCache[_date]['lowest'][field] = {}
			elif field not in self.__minkCache[_date]['lowest'].keys():
				self.__minkCache[_date]['lowest'][field] = {}

			# 将前@days - 1天的最低值存入缓存
			_vPrior = Data.lowestWithinDays(self, _date, days, field, True)
			self.__minkCache[_date]['lowest'][field][days] = _vPrior

			if not exclude:
				# 计入传入tick数据
				_vCur = self.getField(tick, field)
				if _vPrior is None:
					return _vCur
				return min(_vPrior, _vCur)

			return _vPrior

	def highestWithinDays (self, tick, days, field = F_CLOSE, exclude = True):
		"""
		获得交易时间前@days天中最大值
		:param tick: 交易时间
		:param days: 天数
		:param field: 字段
		:param exclude: 传入tick是否计入
		:return: 几天内最低值
		"""
		_date = "%s" % tick.date()
		try:
			_vPrior = self.__minkCache[_date]['highest'][field][days]
			if not exclude:
				# 计入传入tick数据
				_vCur = self.getField(tick, field)
				if _vPrior is None:
					return _vCur
				return max(_vPrior, _vCur)

			return _vPrior
		except KeyError:
			if _date not in self.__minkCache.keys():
				# tick日期发生变化，依据邻近原则更新缓存区
				self.debug.dbg("highestWithinDays: __minkCache: %s" % self.__minkCache)
				self.__minkCache.clear()
				self.__minkCache[_date] = {}
				self.__minkCache[_date]['highest'] = {}
				self.__minkCache[_date]['highest'][field] = {}
			elif 'highest' not in self.__minkCache[_date].keys():
				self.__minkCache[_date]['highest'] = {}
				self.__minkCache[_date]['highest'][field] = {}
			elif field not in self.__minkCache[_date]['highest'].keys():
				self.__minkCache[_date]['highest'][field] = {}

			# 将前@days - 1天的最大值存入缓存
			_vPrior = Data.highestWithinDays(self, _date, days, field, True)
			self.__minkCache[_date]['highest'][field][days] = _vPrior

			if not exclude:
				# 计入传入tick数据
				_vCur = self.getField(tick, field)
				if _vPrior is None:
					return _vCur
				return max(_vPrior, _vCur)

			return _vPrior

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


def doTestData():
	"""
	Data测试
	"""
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


def doTestDataMink():
	"""
	DataMink测试
	"""
	import core.corecfg
	descCfg = core.corecfg.ContractDescConfig('../config/contracts_desc')
	data = DataMink('p1405_mink', descCfg, False)

	date = DataMink.dateConverter('2014-03-11 14:36:00')
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

	date = DataMink.dateConverter('2013-05-16 9:01:00')
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

	date = DataMink.dateConverter('2014-04-30 14:58:00')
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
	Test Middle: Date: 2014-03-11 14:36:00
	M: 6398.0
	M5: 6306.8
	M10: 6221.8
	M20: 6129.6
	M30: 6014.73333333
	Open: 6400.0
	Close: 6398.0
	Avg: 0.0
	High: 6402.0
	Low: 6398.0
	Highest Before: exclude 6328.0, not exclude 6398.0
	Lowest Before: exclude 6102.0, not exclude 6102.0
	Test Left Bound: Date: 2013-05-16 09:01:00
	M: 6246.0
	M5: 6246.0
	M10: 6246.0
	M20: 6246.0
	M30: 6246.0
	Open: 6246.0
	Close: 6246.0
	Avg: 0.0
	High: 6246.0
	Low: 6246.0
	Highest Before: exclude None, not exclude 6246.0
	Lowest Before: exclude None, not exclude 6246.0
	Test Right Bound: Date: 2014-04-30 14:58:00
	M: 5876.0
	M5: 5912.0
	M10: 5930.4
	M20: 5963.6
	M30: 6001.73333333
	Open: 5878.0
	Close: 5876.0
	Avg: 0.0
	High: 5878.0
	Low: 5876.0
	Highest Before: exclude 6002.0, not exclude 6002.0
	Lowest Before: exclude 5900.0, not exclude 5876.0
	"""


if __name__ == '__main__':
	doTestData()
	doTestDataMink()
