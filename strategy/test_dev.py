#! /usr/bin/python
#-*- coding:utf-8 -*-

'''
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2015年 05月 28日 星期四 22:36:48 CST

开发测试模块
'''

import sys
sys.path.append("..")

from core.futures import *
# from core.parallel import *

#
class TestFuture(Futures):
	def __init__ (self, 
		contract, 	#合约
		config,		#合约配置解析接口
		logDir,		#日志目录
		debug = False,	#是否调试
		):
		#
		Futures.__init__(self, contract, config, logDir, debug)
		self.lossProtected = False	#止损保护
		self.initStatFrame(tkCols = ['LossProt'])

	#
	def tradeStoreTickEnv (self):
		env = [self.lossProtected]
		return env

	#
	def tradeResumeTickEnv (self, values):
		self.lossProtected = values['LossProt']
		self.debug.warn("tradeResumeTickEnv: lossProtected %s" % self.lossProtected)

	#开始交易信号
	def signalStartTrading (self,
		tick,	#交易时间
		):
		price = self.data.getClose(tick)
		
		#忽略交易的前20天
		if self.tickHelper.getTickIndex(tick) < 20:
			self.debug.dbg("tick %s index %s" % (tick, self.tickHelper.getTickIndex(tick)))
			return None
		
		if price < self.data.lowestWithinDays(tick, 20):
			#20内新低，开空信号
			self.log("%s Hit Short Signal: Close %s, Lowest %s, priceVariation %d" % (
					tick, price, self.data.lowestWithinDays(tick, 20), self.attrs.priceVariation))
			return SIG_TRADE_SHORT
		elif price > self.data.highestWithinDays(tick, 20):
			#20内新高，开多信号
			self.log("%s Hit Long Signal: Close %s, Highest %s, priceVariation %d" % (
					tick, price, self.data.highestWithinDays(tick, 20), self.attrs.priceVariation))
			return SIG_TRADE_LONG
		else:
			#不触发信号
			return None
	
	#结束交易信号
	def signalEndTrading (self,
		tick,		#交易时间
		direction,	#多空方向
		):
		price = self.data.getClose(tick)
		ret = False
		
		if direction == SIG_TRADE_SHORT and price > self.data.highestWithinDays(tick, 10):
			#价格创出10日新高，结束做空
			self.log("	[Short] [%s] Hit Highest in 10 days: Clear all!: close %s, highest %d" % (
						tick, price, self.data.highestWithinDays(tick, 10)))
			ret = True
		elif direction == SIG_TRADE_LONG and price < self.data.lowestWithinDays(tick, 10):
			#价格创出10日新低，结束做多
			self.log("	[Long] [%s] Hit Lowest in 10 days: Clear all!: close %s, lowest %d" % (
						tick, price, self.data.lowestWithinDays(tick, 10)))
			ret = True
		else:
			return ret
	
		#交易结束，退出止损保护
		self.lossProtected = False
	
		return ret

	#止损信号
	def signalCutLoss (self,
		tick,		#交易时间
		direction,	#多空方向
		):
		#已经止损过，不再重复止损
		if self.lossProtected:
			return False
		
		price = self.data.getClose(tick)
		ret = False
		
		if direction == SIG_TRADE_SHORT and price > self.data.M10(tick):
			#价格高于M10，做空止损
			self.log("	[Short] [%s] cut loss, M10:	close %s, M10 %s" % (
						tick, price, self.data.M10(tick)))
			ret = True
		elif direction == SIG_TRADE_LONG and price < self.data.M10(tick):
			#价格低于M10，做多止损
			self.log("	[Long] [%s] cut loss, M10:	close %s, M10 %s" % (
						tick, price, self.data.M10(tick)))
			ret = True
		else:
			return ret
		
		#设置止损保护标志
		self.lossProtected = True
		
		return ret
	
	#加仓信号
	def signalAddPosition (self,
		tick,		#交易时间
		direction,	#多空方向
		):
		#如果仓位已满，则不再加仓
		if self.curPositions() >= self.attrs.maxPosAllowed:
			self.debug.dbg("Current positions reaches the highest limit %s!" % (
						self.attrs.maxPosAllowed))
			return False
		
		price = self.data.getClose(tick)
		#得到最后一仓价格
		lastPosPrice = self.getPosition().price
		#触发加仓的价差
		interval = self.attrs.priceVariation
		ret = False
		
		if direction == SIG_TRADE_SHORT and lastPosPrice - price > interval:
			#做空，价格满足价差，加仓
			self.log("	[Short] [%s] add postion	last add %s,  close %s, intv %d" % (
						tick, lastPosPrice, price, lastPosPrice-price))
			ret = True
		elif direction == SIG_TRADE_LONG and price - lastPosPrice > interval:
			#做多，价格满足价差，加仓
			self.log("	[Long] [%s] add postion	last add %s,  close %s, intv %d" % (
						tick, lastPosPrice, price, price-lastPosPrice))
			ret = True
		else:
			return ret
		
		#加仓，退出止损保护
		self.lossProtected = False
		
		return ret
	
	#止损
	#override
	def tradeCutLoss (self,
		tick,		#交易时间
		direction,	#方向
		):
		#止损减去总仓位的2/3
		num = self.curPositions()*2/3
		if num == 0:
			num = 1
		
		price = self.data.getClose(tick)
		
		self.debug.dbg("tradeCutLoss: %s, price %s, positions to cut %s" % (
				tick, price, num))
		
		return self.closePositions(tick, price, direction, num)
#
# #
# def testParallelThreadEntry (
# 	strategy,	#
# 	):
# 	strategy.start()
#
# #测试
# def doTest():
# 	tf = TestFuture('p1405', 'p1405_dayk', 'history', True)
# 	paraCore = ParallelCore('2013-05-16', 15, 6, 3, 'test4_para', True)
#
# 	tf.setAttrs(maxPosAllowed = 4,
# 			numPosToAdd = 1,
# 			priceVariation = 40,
# 			multiplier = 10,
# 			dumpName = 'test4',
# 			paraCore = paraCore)
#
# 	paraCore.allocManager("p1405")
# 	paraCore.setSyncWindowForContracts()
# 	thread.start_new_thread(testParallelThreadEntry, (tf,))
# 	paraCore.handleActions()
#
#
# if __name__ == '__main__':
# 	doTest()
#
#