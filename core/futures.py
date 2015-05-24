#-*- coding:utf-8 -*-

'''
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2015年 05月 23日 星期六 23:51:07 CST

期货回归测试、交易核心模块

原有期货交易模块(strategy/futures.py)有诸多缺点，比如交易框架不明确、
成员属性功能等管理杂乱、统计功能独立性不强，导致在策略开发时代码冗余过
多，不利于稳定，并且长期维护困难。新模块将重新定义交易框架，会集成统计
模块到通用接口，避免在子策略中做统计，让策略开发变得简单。另外会持续集
成老模块中的优良部分进来。
'''

import sys
sys.path.append("..")

from dataMgr.data import *
from ctp.autopos import *
from misc.posmgr import *
from misc.debug import *
from date import *
from attribute import *
from signal import *
from statistics import *

#期货类
class Futures:
	
	attrs 	= Attribute()		#属性
	posMgr	= None			#持仓管理接口
	
	def __init__ (self, 
		contract, 	#合约
		table, 		#数据表名
		database, 	#数据库名
		debug = False,	#是否调试
		):
		self.contract = contract
		self.database = database
		self.table = table
		self.debug = Debug('Futures', debug)	#调试接口
		self.data = Data(database, table)	#数据接口
		self.cs = ContractStat(contract, debug)	#数据统计接口

	'''
	属性方法
	'''
	
	#设置属性
	def setAttrs (self, 
		maxPosAllowed,	#最大允许持仓／加仓（单位）数量
		numPosToAdd,	#每次加仓（单位）数量
		priceVariation,	#加仓条件触发价格差
		muliplier,	#合约乘数
		):
		self.attrs.set(maxPosAllowed = maxPosAllowed,
				numPosToAdd = numPosToAdd,
				priceVariation = priceVariation,
				muliplier = muliplier)
		
		#初始化持仓管理接口
		self.posMgr = PositionMananger(maxPosAllowed)
		
	#检查属性
	def checkAttrs (self):
		#默认属性无误
		return True
	
	'''
	持仓方法
	'''
	
	#返回当前仓位
	def curPositions (self):
		return self.posMgr.numPositions()
	
	#清空持仓
	def clearPositions (self):
		return self.posMgr.empty()
	
	#返回第num个仓位，num从１开始记
	def getPosition (self, 
		num = None,	#仓位标号
		):
		#默认（num为None）返回最后一个仓位
		if not num:
			num = self.posMgr.numPositions()
			
		return self.posMgr.getPosition(num)
	
	#开仓
	def openPositions (self, 
		tick,		#时间
		price,		#价格
		direction,	#方向
		volume = 1,	#开仓量
		):
		#如果加仓失败返回False
		if not self.posMgr.pushPosition(tick, price, volume, direction):
			return False
		
		self.log("		-->> Open: %s, poses %s <<--" % (
						price, self.curPositions()))
	
		return True
	
	#平仓
	def closePositions (self, 
		tick,		#时间
		price,		#价格
		direction,	#方向
		numPos = 1,	#单位数
		):
		#如果仓位不足，不允许操作
		if numPos > self.curPositions():
			self.debug.error("Required %s, but only %s in Position Manager!" % (
						numPos, self.curPositions()))
			return False
		
		#从第一仓开始按序减仓
		i = 0
		while i < numPos:
			#移除仓位并计算利润
			pos = self.posMgr.popPosition(1)
			if direction == SIG_TRADE_SHORT:
				orderProfit = pos.price - price
			else:
				orderProfit = price - pos.price
			
			#单价获利x每单手数x合约乘数
			orderProfit *= self.attrs.numPosToAdd
			orderProfit *= self.attrs.muliplier
			
			#更新平仓利润信息
			self.cs.update(orderProfit)
			
			self.log("		<<-- Close: open %s, close %s, profit %s -->>" % (
							pos.price, price, orderProfit))
			
			i += 1
		
		#如果平仓后仓位为０说明本次交易结束。打印统计信息并重置。
		if self.curPositions() == 0:	
			self.__reset()
		
		return True
	
	#打印统计信息,并重置利润
	def __reset (self):
		self.log("		++++++ Business profit %s ++++++" % (
							self.cs.profit.getCurrent()))
		self.log("		****** Total profit %s ******" % (
							self.cs.profit.getSum()))
		self.cs.profit.reset()
	
	'''
	交易方法
	'''
	
	#开始交易信号
	def signalStartTrading (self,
		tick,	#交易时间
		):
		return None
	
	#结束交易信号
	def signalEndTrading (self,
		tick,		#交易时间
		direction,	#多空方向
		):
		return False
	
	#止损信号
	def signalCutLoss (self,
		tick,		#交易时间
		direction,	#多空方向
		):
		return False
	
	#加仓信号
	def signalAddPosition (self,
		tick,		#交易时间
		direction,	#多空方向
		):
		return False
	
	#止赢信号
	def signalStopProfit (self,
		tick,		#交易时间
		direction,	#多空方向
		):
		return False
	
	#交易信号是否有效
	def __validStartSignal (self,
		signal,	#交易信号
		):
		if signal is None:
			return False
		elif signal == SIG_TRADE_LONG or signal == SIG_TRADE_SHORT:
			return True
		else:
			return False
	
	#交易信号转换成方向字符串
	def __signalToDirection (self,
		signal,	#交易信号
		):
		if signal == SIG_TRADE_SHORT:
			return 'Short'
		elif signal == SIG_TRADE_LONG:
			return 'Long'
		else:
			return None

	#交易开始
	def tradeStart (self,
		startTick,	#开始交易时间
		signal,		#交易信号／方向
		):
		self.debug.dbg("Start Trading: [%s][%s]" % (
					self.__signalToDirection(signal), startTick))
		
		#使用独立交易时间管理接口，保持独立性，避免互相影响。
		tick = Ticks(self.database, self.table)
		tick.setCurTick(startTick)
		#交易信号已经触发，先入仓
		self.tradeAddPositions(startTick, signal)
		#得到tick中的下一交易时间
		nextTick = self.tradeNextTick(tick, startTick)

		#除非到数据表结尾或交易退出，否则一直交易
		while nextTick is not None:
			if self.signalEndTrading(nextTick, signal):
				#触发退出交易信号
				self.debug.dbg("End Trading: [%s][%s]" % (
							self.__signalToDirection(signal), nextTick))
				self.tradeEnd(nextTick, signal)
				#返回触发退出信号的当前tick
				return nextTick
				
			elif self.signalCutLoss(nextTick, signal):
				#触发止损信号
				self.debug.dbg("Cut Loss: [%s][%s]" % (
							self.__signalToDirection(signal), nextTick))
				self.tradeCutLoss(nextTick, signal)
				#如果止损后仓位为０，说明交易结束，返回当前tick
				if self.curPositions() == 0:
					return nextTick
				
			elif self.signalAddPosition(nextTick, signal):
				#触发加仓信号
				self.debug.dbg("Add Position: [%s][%s]" % (
							self.__signalToDirection(signal), nextTick))
				self.tradeAddPositions(nextTick, signal)
				
			elif self.signalStopProfit(nextTick, signal):
				#触发止赢信号
				self.debug.dbg("Stop Profit: [%s][%s]" % (
							self.__signalToDirection(signal), nextTick))
				self.tradeStopProfit(nextTick, signal)
			
			#下一tick继续
			nextTick = self.tradeNextTick(tick, nextTick)
		
		#正常应该以交易结束返回对应tick，如果nextTick为
		#None说明执行到表尾，返回None
		return None

	#加仓
	def tradeAddPositions (self,
		tick,		#交易时间
		direction,	#方向
		):
		price = self.data.getClose(tick)
		volume = self.attrs.numPosToAdd
		
		self.debug.dbg("Add position tick %s, price %s, volume %s, direction %s" % (
						tick, price, volume, direction))
		
		#开仓
		self.openPositions(tick, price, volume, direction)
		
	#止损
	#MUST_OVERRIDE
	def tradeCutLoss (self,
		tick,		#交易时间
		direction,	#方向
		):
		return
	
	#止赢
	#MUST_OVERRIDE
	def tradeStopProfit (self,
		tick,		#交易时间
		direction,	#方向
		):
		return
	
	#停止交易
	def tradeEnd (self,
		tick,		#交易时间
		direction,	#方向
		):
		#停止交易，清空所有仓位
		self.closePositions(tick = tick, 
				price = self.data.getClose(tick), 
				direction = direction, 
				numPos = self.curPositions())
	
	#开始测试／交易
	def start (self):
		#使用独立交易时间管理接口，保持独立性，避免互相影响。
		tick = Ticks(self.database, self.table)
		curTick = tick.firstTick()
		
		#除非到数据表结尾，否则一直交易
		while curTick is not None:
			#检测是否触发交易信号
			signal = self.signalStartTrading(curTick)
			if not self.__validStartSignal(signal):
				curTick = self.tradeNextTick(tick, curTick)
				continue
			
			'''
			触发交易信号，交易开始
			'''
			
			#开始交易，并返回交易结束时的当前tick
			endTick = self.tradeStart(curTick, signal)
			#如果返回的tick为空则表示已到数据表末尾
			if endTick is None:
				break
				
			#返回tick不为空，则继续下一tick
			curTick = self.tradeNextTick(tick, endTick)
		
		#结束交易，清空仓位
		self.tradeEnd(tick.lastTick(), signal)
		#执行结束，显示统计信息
		self.cs.show()
	
	#返回下一交易时间
	def tradeNextTick (self, 
		tickObj,	#tick接口对象
		tick,		#当前tick
		):
		tickObj.setCurTick(tick)
		return tickObj.getSetNextTick()
	
	#日志（输出）统一接口
	def log (self, 
		logMsg,	#日志消息
		*args	#参数
		):
		logs = logMsg % (args)
		print logs
	
	