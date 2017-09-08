# -*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2017年 06月 19日 星期一 22:49:45 CST

"""

import sys
sys.path.append("..")
import numpy as np

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

		self.initStatFrame(tkCols = ['FloatRatio', "OP2_FR"],
			trdCols = ["FR_Min", "FR_Max", "PFR", "OP2_FR_Min", "OP2_FR_Max", "OP2_PFR"])
		self.firstTick = self.tickHelper.firstTick()
		#
		self.opPrice1 = self.opPrice2 = None

	def validSignal(self, tick):
		ret = True
		if tick - self.firstTick < timedelta(days = 10):
			ret = False

		return ret

	def __curFloatRate(self, price, opPrice, direction):
		"""
		计算当前浮动利润率
		:param price: 当前价格
		:param direction: 方向
		:param opPrice: 加仓价格
		:return: 浮动利润率|NaN
		"""
		ret = np.nan
		if not opPrice:
			return ret

		if direction == SIG_TRADE_LONG:
			ret = (price - opPrice) / opPrice
		elif direction == SIG_TRADE_SHORT:
			ret = (opPrice - price) / opPrice

		return ret

	def storeCustomTickEnv(self, tick, price, direction):
		"""
		追加需在tickStatFrame记录的数据，私有变量、统计数据等
		:param tick: 当前tick
		:param price: 当前价格
		:param direction: 方向
		:return: 数据列表
		"""
		ret = list()

		for p in (self.opPrice1, self.opPrice2):
			_cfr = self.__curFloatRate(price, p, direction)
			ret.append(_cfr)

		return ret

	def storeCustomTradeEnv(self, tick, price, direction):
		"""
		:param tick: 交易时间
		:param price: 成交价
		:param direction: 多空方向
		:return: 数据列表
		"""
		ret = list()
		todo = (("FloatRatio", self.opPrice1), ("OP2_FR", self.opPrice2))

		for col, opPrice in todo:
			_val = self.tickStatFrame[self.tickStatFrame[col].notnull()][col]
			if _val.empty:
				ret += [np.nan] * 3
				continue

			desc = _val.describe()
			_min = desc["min"]
			_max = desc["max"]
			pfr = self.__curFloatRate(price, opPrice, direction)
			ret += [_min, _max, pfr]

		#
		self.opPrice1 = self.opPrice2 = None
		return ret

	def signalStartTrading(self, tick):
		"""
		触发开始交易信号
		:param tick: 交易时间
		:return: SIG_TRADE_SHORT、SIG_TRADE_LONG、None
		"""
		ret = None
		if not self.validSignal(tick):
			return ret

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
			self.opPrice1 = price

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

	def signalAddPosition(self, tick, direction):
		"""
		触发加仓信号
		:param tick: 交易时间
		:param direction: 多空方向
		:return: 触发加仓信号返回True，否则返回False
		"""
		ret = False
		price = self.data.getClose(tick)
		pos = self.getPosition()

		cfr = self.__curFloatRate(price, pos.price, direction)
		if cfr >= 0.01 and self.curPositions() < 2:
			#
			self.log("	Add Position: %s, cfr %s" % (tick, cfr))
			self.opPrice2 = price
			ret = True

		return ret

	def signalCutLoss(self, tick, direction):
		"""
		触发止损信号
		:param tick: 交易时间
		:param direction: 多空方向
		:return: 触发止损信号返回True，否则返回False
		"""
		ret = False
		price = self.data.getClose(tick)

		cfr = self.__curFloatRate(price, self.opPrice1, direction)
		if cfr < -0.016:
			#
			self.log("	Cut Loss: %s, cfr %s" % (tick, cfr))
			ret = True

		return ret

	def tradeCutLoss(self, tick, direction):
		"""
		止损。必须被重载实现
		@MUST_OVERRIDE
		:param tick: 交易时间
		:param direction: 方向
		:return: 成功返回True，否则返回False
		"""
		price = self.data.getClose(tick)
		ret = self.closePositions(tick, price, direction, self.curPositions())
		return ret
