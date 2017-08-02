# -*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2017年 06月 19日 星期一 22:49:45 CST

"""

import sys
sys.path.append("..")

from datetime import datetime, timedelta
from core.futures import *
from db.tbldesc import *


class Main(Futures):
	def __init__(self, contract, config, logDir, debug = False):
		"""
		采集数据
		:param contract: 合约
		:param config: 合约配置解析接口
		:param logDir: 日志目录
		:param debug: 是否调试
		"""
		Futures.__init__(self, contract, config, logDir, debug)
		self.debug = Debug("Discover", debug)

		self.initStatFrame(tkCols = ['FloatRatio'], trdCols = ["FR_Min", "FR_Max", "PFR"])
		self.firstTick = self.tickHelper.firstTick()
		#
		self.opPrice = 0

	def invalidSignal(self, tick):
		if tick - self.firstTick < timedelta(days = 10):
			return False

		return True

	def __curFloatRate(self, price, direction):
		"""
		计算当前浮动利润率
		:param price: 当前价格
		:param direction: 方向
		:return: 浮动利润率
		"""
		ret = 0
		if direction == SIG_TRADE_LONG:
			ret = (price - self.opPrice)/self.opPrice
		elif direction == SIG_TRADE_SHORT:
			ret = (self.opPrice - price)/self.opPrice

		return ret

	def storeCustomTickEnv(self, tick, price, direction):
		"""
		追加需在tickStatFrame记录的数据，私有变量、统计数据等
		:param tick: 当前tick
		:param price: 当前价格
		:param direction: 方向
		:return: 数据列表
		"""
		ret = self.__curFloatRate(price, direction)
		return [ret]

	def storeCustomTradeEnv(self, tick, price, direction):
		"""
		:param tick: 交易时间
		:param price: 成交价
		:param direction: 多空方向
		:return: 数据列表
		"""
		desc = self.tickStatFrame["FloatRatio"].describe()
		_min = desc["min"]
		_max = desc["max"]
		pfr = self.__curFloatRate(price, direction)
		return [_min, _max, pfr]

	def signalStartTrading(self, tick):
		"""
		触发开始交易信号
		:param tick: 交易时间
		:return: SIG_TRADE_SHORT、SIG_TRADE_LONG、None
		"""
		ret = None
		if not self.invalidSignal(tick):
			return None

		days = 15
		price = self.data.getClose(tick)
		if price < self.data.lowestWithinDays(tick, days):
			# 20内新低，开空信号
			self.log("%s Hit Short Signal: Close %s, Lowest %s, priceVariation %d" % (
				tick, price, self.data.lowestWithinDays(tick, days), self.attrs.priceVariation))
			ret = SIG_TRADE_SHORT

		elif price > self.data.highestWithinDays(tick, days):
			# 20内新高，开多信号
			self.log("%s Hit Long Signal: Close %s, Highest %s, priceVariation %d" % (
				tick, price, self.data.highestWithinDays(tick, days), self.attrs.priceVariation))
			ret = SIG_TRADE_LONG

		if ret:
			self.opPrice = price

		return ret

	def signalEndTrading(self, tick, direction):
		"""
		触发结束交易信号
		:param tick: 交易时间
		:param direction: 多空方向
		:return: 触发结束信号返回True，否则返回False
		"""
		ret = False
		days = 10
		price = self.data.getClose(tick)

		if direction == SIG_TRADE_SHORT and \
			price > self.data.highestWithinDays(tick, days):
			# 价格创出10日新高，结束做空
			self.log("	[Short] [%s] Hit Highest in %s days: Clear all!: close %s, highest %d" % (
						tick, days, price, self.data.highestWithinDays(tick, days)))
			ret = True

		elif direction == SIG_TRADE_LONG and \
			price < self.data.lowestWithinDays(tick, days):
			# 价格创出10日新低，结束做多
			self.log("	[Long] [%s] Hit Lowest in %s days: Clear all!: close %s, lowest %d" % (
						tick, days, price, self.data.lowestWithinDays(tick, days)))
			ret = True

		return ret
