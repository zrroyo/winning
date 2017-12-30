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
		self.tkCols = ["OP1_FR", "OP2_FR", "OP3_FR", "OP4_FR"]
		self.initStatFrame(tkCols = self.tkCols, trdCols = ["TRD_ID"])
		self.firstTick = self.tickHelper.firstTick()
		#
		self.opPrice = list()
		#
		self.toCutLoss = None
		#
		self.pLastCut = None
		#
		self.posStatFrame = pd.DataFrame()

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
		# 统计的数据列受tkCols控制
		_maxPos = len(self.tkCols)

		for i in range(_maxPos):
			try:
				p = self.opPrice[i]
			except IndexError, e:
				p = None
			_cfr = self.__curFloatRate(price, p, direction)
			ret.append(_cfr)

		if self.toCutLoss:
			# 已发生止损，仓位已平，缓存的开仓使用完毕需移除，避免下一tick重复记入
			self.opPrice = self.opPrice[:self.toCutLoss-1]
			# toCutLoss仅用于保证止损时能得到开仓价并计算出pfr，用完需清除避免影响下一tick
			self.toCutLoss = None

		if self.curPositions() == 0:
			# 交易已经结束
			self.opPrice = list()

		return ret

	def __genTradeStat(self, direction, col, stCol):
		"""
		生成(各仓位的)交易统计数据
		:param direction: 多空方向
		:param col: 目标列
		:param stCol: 统计列
		:return: 统计数据矩阵
		"""
		val = self.tickStatFrame[[col]]
		oldIndex = val.index
		val.index = range(len(val))
		# val.to_excel("/tmp/genTradeStat_val.xls")
		nnIdx = set(val[val[col].notnull()].index)
		# 得到有效的数值区间
		_index = val.index
		val.index = list(_index[1:]) + [_index[-1] + 1]
		isnIdx1 = set(val[val[col].isnull()].index)
		val.index = [-1] + list(_index[:-1])
		isnIdx2 = set(val[val[col].isnull()].index)
		val.index = _index
		_ceiling = sorted(list(nnIdx.intersection(isnIdx1)))
		_floor = sorted(list(nnIdx.intersection(isnIdx2)))

		if len(_ceiling) == 0 or len(_floor) == 0:
			# 上沿为空、下沿为空或都为空的情况下数据区间唯一
			todo = [val[val[col].notnull()]]
		else:
			_bound = list()
			if _floor[0] < _ceiling[0]:
				# 第一个数据区间从‘0’索引开始
				_bound.append((0, _floor[0]))
				_floor = _floor[1:]

			if _ceiling[-1] > _floor[-1]:
				# 最后一个数据区间到结束
				_floor += [_index[-1]]

			_bound += zip(_ceiling, _floor)
			todo = map(lambda x: val.iloc[x[0]: x[1]+1], _bound)

		_ret = list()
		for t in todo:
			if t.empty:
				_ret.append([np.nan] * len(stCol))
				continue

			desc = t[col].describe()
			_min = desc["min"]
			_max = desc["max"]
			# 数据区间中的第一个为开仓tick，价格即为开仓价
			_opTick = oldIndex[t.index[0]]
			_endTick = oldIndex[t.index[-1]]
			_opPrice = self.data.getClose(_opTick)
			_endPrice = self.data.getClose(_endTick)
			profit = self.orderProfit(direction, _opPrice, _endPrice)
			pfr = t.iloc[-1][col]
			_ret.append([_opTick, _opPrice, _endTick, _endPrice, _min, _max, pfr,
				profit, (pfr - _max)])

		ret = pd.DataFrame(_ret, columns = stCol)
		return ret

	def storeCustomTradeEnv(self, tick, price, direction):
		"""
		:param tick: 交易时间
		:param price: 成交价
		:param direction: 多空方向
		:return: 数据列表
		"""
		trdID = "%s_%s" % (self.contract, len(self.trdStatFrame) + 1)
		todo = {
			'OP1_FR': ["OP1_OP_TICK", "OP1_OP_PRICE", "OP1_CLS_TICK", "OP1_CLS_PRICE",
				"OP1_FR_Min", "OP1_FR_Max", "OP1_PFR", "OP1_PROFIT", "OP1_FR_DD"],
			'OP2_FR': ["OP2_OP_TICK", "OP2_OP_PRICE", "OP2_CLS_TICK", "OP2_CLS_PRICE",
				"OP2_FR_Min", "OP2_FR_Max", "OP2_PFR", "OP2_PROFIT", "OP2_FR_DD"],
			'OP3_FR': ["OP3_OP_TICK", "OP3_OP_PRICE", "OP3_CLS_TICK", "OP3_CLS_PRICE",
				"OP3_FR_Min", "OP3_FR_Max", "OP3_PFR", "OP3_PROFIT", "OP3_FR_DD"],
			'OP4_FR': ["OP4_OP_TICK", "OP4_OP_PRICE", "OP4_CLS_TICK", "OP4_CLS_PRICE",
				"OP4_FR_Min", "OP4_FR_Max", "OP4_PFR", "OP4_PROFIT", "OP4_FR_DD"],
			'OP5_FR': ["OP5_OP_TICK", "OP5_OP_PRICE", "OP5_CLS_TICK", "OP5_CLS_PRICE",
				"OP5_FR_Min", "OP5_FR_Max", "OP5_PFR", "OP5_PROFIT", "OP5_FR_DD"]
			}

		ret = pd.DataFrame()
		for c in self.tkCols:
			cols = todo[c]
			_ret = self.__genTradeStat(direction, c, cols)
			ret = pd.concat([ret, _ret], axis = 1)

		# 插入交易号
		ret = pd.concat([pd.DataFrame(pd.Series([trdID] * len(ret)), columns=['TRD_ID']), ret], axis = 1)
		#
		self.posStatFrame = self.posStatFrame.append(ret, ignore_index = True)
		#
		self.opPrice = list()
		#
		return [trdID]

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
			self.opPrice.append(price)

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
		thresholds = [None, 0.013]
		price = self.data.getClose(tick)
		pos = self.getPosition()

		if self.pLastCut:
			# 需保证新开仓价优于最近一次止损价，否则会有止损点无效风险
			if (direction == SIG_TRADE_LONG and price <= self.pLastCut) or (\
				direction == SIG_TRADE_SHORT and price >= self.pLastCut):
				return ret

		try:
			_thr = thresholds[self.curPositions()]
			cfr = self.__curFloatRate(price, pos.price, direction)
			# 利润浮动需大于仓位对应阈值，并且需大于该仓位上一次开仓价（否则会导致止损失效）
			if cfr >= _thr:
				self.log("	Add Position: %s, cfr %s" % (tick, cfr))
				self.opPrice.append(price)
				# 止损后才需设置以预防止损失效
				self.pLastCut = None
				ret = True
		except IndexError, e:
			ret = False

		return ret

	def signalCutLoss(self, tick, direction):
		"""
		触发止损信号
		:param tick: 交易时间
		:param direction: 多空方向
		:return: 触发止损信号返回True，否则返回False
		"""
		price = self.data.getClose(tick)
		thresholds = [-0.016, -0.013]
		# thresholds = []
		self.toCutLoss = None
		cfr = list()

		for posIdx in range(1, self.curPositions() + 1):
			pos = self.getPosition(posIdx)
			_cfr = self.__curFloatRate(price, pos.price, direction)
			try:
				_thr = thresholds[posIdx - 1]
				cfr.append(_cfr)
				if _cfr < _thr:
					self.toCutLoss = posIdx
					# 记录止损点，作为加仓条件以避免止损无效
					self.pLastCut = pos.price
					break
			except IndexError, e:
				break

		ret = False
		if self.toCutLoss:
			self.log("	Cut Loss: %s, price %s, cut from %s, cfr %s" % (
						tick, price, self.toCutLoss, cfr))
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
		nrPos = self.curPositions() - self.toCutLoss + 1
		ret = self.closePositions(tick, price, direction, nrPos, reverse = True)
		return ret

	def customExit(self):
		"""

		:return: None
		"""
		# 将tick数据以excel格式保存
		_data = "%s/%s" % (self.logDir, self.contract)
		self.posStatFrame.to_excel("%s_POS_STAT.xlsx" % _data, float_format = "%.5f")
