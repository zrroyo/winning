#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2015年 05月 23日 星期六 23:51:07 CST

期货回归测试、交易核心模块

原有期货交易模块(strategy/futures.py)有诸多缺点，比如交易框架不明确、
成员属性功能等管理杂乱、统计功能独立性不强，导致在策略开发时代码冗余过
多，不利于稳定，并且长期维护困难。新模块将重新定义交易框架，会集成统计
模块到通用接口，避免在子策略中做统计，让策略开发变得简单。另外会持续集
成老模块中的优良部分进来。
"""

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
from parallel import *

# 期货类
class Futures:
	
	attrs = Attribute()	#属性
	posMgr = None		#持仓管理接口
	
	def __init__ (self, 
		contract, 	#合约
		table, 		#数据表名
		database, 	#数据库名
		debug = False,	#是否调试
		):
		self.dbgMode = debug
		self.contract = contract
		self.database = database
		self.table = table
		self.debug = Debug('Futures', debug)	#调试接口
		self.data = Data(database, table)	#数据接口
		self.tickSrc = Ticks(self.database, self.table)	#Tick接口
		# 当前tick是否已经被处理过
		self.tagTickParaHandled = False
	
	# ----------------
	# 属性方法
	# ----------------
	
	# 设置属性
	def setAttrs (self, 
		maxPosAllowed,		#最大允许持仓单位数
		numPosToAdd,		#每加仓单位所代表的手数
		priceVariation,		#触发加仓条件的价格差
		multiplier,		#合约乘数
		dumpName = None,	#统计信息Dump名
		paraCore = None,	#并行处理接口实例
		):
		self.attrs.set(maxPosAllowed = maxPosAllowed,
				numPosToAdd = numPosToAdd,
				priceVariation = priceVariation,
				multiplier = multiplier)
		
		# 初始化持仓管理接口
		self.posMgr = PositionMananger(maxPosAllowed)
		# 数据统计接口
		self.cs = ContractStat(self.contract, dumpName, self.dbgMode)
		
		# 如果使能了并行模拟，则需要为合约初始化
		self.paraCore = paraCore
		if paraCore != None:
			self.paraCore.allocManager(self.contract)
	
	# 检查属性
	def checkAttrs (self):
		# 默认属性无误
		return True
	
	# ----------------
	# 持仓方法
	# ----------------
	
	# 返回当前仓位
	def curPositions (self):
		return self.posMgr.numPositions()
	
	# 清空持仓
	def clearPositions (self):
		return self.posMgr.empty()
	
	# 返回第num个仓位，num从１开始记
	def getPosition (self, 
		num = None,	#仓位标号
		):
		# 默认（num为None）返回最后一个仓位
		if not num:
			num = self.posMgr.numPositions()
			
		return self.posMgr.getPosition(num)
	
	# 发送并行处理请求
	def __sendParaRequest (self,
		tick,			#时间
		type,			#操作类型
		price,			#价格
		volume,			#开仓手数
		direction,		#方向
		closeProfit = 0,	#平仓利润
		):
		if not self.paraCore or self.tagTickParaHandled:
			# 并行处理未使能或已并行处理过，则不处理
			return True
		
		# 该tick已经并行处理过
		self.tagTickParaHandled = True
		# 计算浮动利润
		floatProfit = self.__floatingProfit(direction, price)
		# 判定是否为最后一个tick
		isLastTick = self.tickSrc.isLastTick(tick)
		# 发送并行处理请求
		if not self.paraCore.request(self.contract, tick, type, price, 
				volume, direction, floatProfit, closeProfit, isLastTick):
			# 申请并行处理失败
			return False
		
		# 申请成功
		return True
	
	# 开仓
	def openPositions (self, 
		tick,		#时间
		price,		#价格
		direction,	#方向
		volume = 1,	#开仓量
		):
		# 发送并行处理请求
		if not self.__sendParaRequest(tick, ACTION_OPEN, price, volume, direction):
			return False
		
		# 如果加仓失败返回False
		if not self.posMgr.pushPosition(tick, price, volume, direction):
			return False
		
		self.log("		-->> Open: %s, poses %s <<--" % (
						price, self.curPositions()))
	
		return True
	
	# 平仓
	def closePositions (self, 
		tick,		#时间
		price,		#价格
		direction,	#方向
		numPos = 1,	#单位数
		):
		# 如果仓位不足，不允许操作
		if numPos > self.curPositions():
			self.debug.error("closePositions: require %s, but only %s left!" % (
						numPos, self.curPositions()))
			return False
		
		# 从第一仓开始按序减仓
		i = 0
		closeProfit = 0
		while i < numPos:
			# 移除仓位并计算利润
			pos = self.posMgr.popPosition(1)
			orderProfit = self.__orderProfit(direction, pos.price, price)
			closeProfit += orderProfit
			# 更新平仓利润信息
			self.cs.update(tick, price, pos, orderProfit)
			
			self.log("		<<-- Close: open %s, close %s, profit %s -->>" % (
							pos.price, price, orderProfit))
			
			i += 1
			
		# 计算仓数
		volume = self.attrs.numPosToAdd * numPos
		# 发送并行处理请求
		self.__sendParaRequest(tick, ACTION_CLOSE, price, volume, direction, closeProfit)
		
		# 如果平仓后仓位为０说明本次交易结束。打印统计信息并重置。
		if self.curPositions() == 0:
			self.__reset(tick, price, direction)
		
		return True
	
	# 打印统计信息,并重置利润
	def __reset (self,
		tick,		#交易时间
		price,		#当前价
		direction,	#方向
		):
		self.log("              ++++++ Business profit %s ++++++" % (
							self.cs.profit.getFinal()))
		self.log("              ****** Total profit %s ******" % (
							self.cs.profit.getSum()))
		# 仓位清空代表一次交易结束，需要在交易数据
		# 清零之前巡航更新统计数据。
		self.__navigate(tick, price, direction)
		# 完成本次交易统计
		self.cs.end(tick)
	
	# ----------------
	# 交易方法
	# ----------------
	
	# 开始交易信号
	def signalStartTrading (self,
		tick,	#交易时间
		):
		return None
	
	# 结束交易信号
	def signalEndTrading (self,
		tick,		#交易时间
		direction,	#多空方向
		):
		return False
	
	# 止损信号
	def signalCutLoss (self,
		tick,		#交易时间
		direction,	#多空方向
		):
		return False
	
	# 加仓信号
	def signalAddPosition (self,
		tick,		#交易时间
		direction,	#多空方向
		):
		return False
	
	# 止赢信号
	def signalStopProfit (self,
		tick,		#交易时间
		direction,	#多空方向
		):
		return False
	
	# 交易信号是否有效
	def __validStartSignal (self,
		signal,	#交易信号
		):
		if signal is None:
			return False
		elif signal == SIG_TRADE_LONG or signal == SIG_TRADE_SHORT:
			return True
		else:
			return False
	
	# 交易信号转换成方向字符串
	def __signalToDirection (self,
		signal,	#交易信号
		):
		if signal == SIG_TRADE_SHORT:
			return 'Short'
		elif signal == SIG_TRADE_LONG:
			return 'Long'
		else:
			return None

	# 交易开始
	def tradeStart (self,
		startTick,	#开始交易时间
		signal,		#交易信号／方向
		):
		self.debug.dbg("tradeStart: Start Trading: [%s][%s]" % (
					self.__signalToDirection(signal), startTick))
		
		# 开始交易数据统计
		self.cs.start(startTick)
		
		# 使用独立交易时间管理接口，保持独立性，避免互相影响。
		tick = Ticks(self.database, self.table)
		tick.setCurTick(startTick)
		# 交易信号已经触发，先入仓
		self.tradeAddPositions(startTick, signal)
		# 得到tick中的下一交易时间
		nextTick = self.tradeNextTick(tick, startTick, signal)

		# 除非到数据表结尾或交易退出，否则一直交易
		while nextTick is not None:
			if self.signalEndTrading(nextTick, signal):
				# 触发退出交易信号
				self.debug.dbg("tradeStart: End Trading: [%s][%s]" % (
							self.__signalToDirection(signal), nextTick))
				self.tradeEnd(nextTick, signal)
				# 返回触发退出信号的当前tick
				return nextTick
				
			elif self.signalCutLoss(nextTick, signal):
				# 触发止损信号
				self.debug.dbg("tradeStart: Cut Loss: [%s][%s]" % (
							self.__signalToDirection(signal), nextTick))
				self.tradeCutLoss(nextTick, signal)
				# 如果止损后仓位为０，说明交易结束，返回当前tick
				if self.curPositions() == 0:
					return nextTick
				
			elif self.signalAddPosition(nextTick, signal):
				# 触发加仓信号
				self.debug.dbg("tradeStart: Add Position: [%s][%s]" % (
							self.__signalToDirection(signal), nextTick))
				self.tradeAddPositions(nextTick, signal)
				
			elif self.signalStopProfit(nextTick, signal):
				# 触发止赢信号
				self.debug.dbg("tradeStart: Stop Profit: [%s][%s]" % (
							self.__signalToDirection(signal), nextTick))
				self.tradeStopProfit(nextTick, signal)
			
			# 下一tick继续
			nextTick = self.tradeNextTick(tick, nextTick, signal)
		
		# 正常应该以交易结束返回对应tick，如果nextTick为
		# None说明执行到表尾，返回None
		return None

	# 加仓
	def tradeAddPositions (self,
		tick,		#交易时间
		direction,	#方向
		):
		price = self.data.getClose(tick)
		volume = self.attrs.numPosToAdd
		
		self.debug.dbg("tradeAddPositions: tick %s, price %s, volume %s, direction %s" % (
						tick, price, volume, direction))
		
		# 开仓
		self.openPositions(tick, price, direction, volume)
		
	# 止损
	# MUST_OVERRIDE
	def tradeCutLoss (self,
		tick,		#交易时间
		direction,	#方向
		):
		return
	
	# 止赢
	# MUST_OVERRIDE
	def tradeStopProfit (self,
		tick,		#交易时间
		direction,	#方向
		):
		return
	
	# 停止交易
	def tradeEnd (self,
		tick,		#交易时间
		direction,	#方向
		):
		#停止交易，清空所有仓位
		self.closePositions(tick = tick, 
				price = self.data.getClose(tick), 
				direction = direction, 
				numPos = self.curPositions())
	
	# 开始测试／交易
	def start (self):
		# 使用独立交易时间管理接口，保持独立性，避免互相影响。
		tick = Ticks(self.database, self.table)
		curTick = tick.firstTick()
		
		# 除非到数据表结尾，否则一直交易
		while curTick is not None:
			# 检测是否触发交易信号
			signal = self.signalStartTrading(curTick)
			if not self.__validStartSignal(signal):
				curTick = self.tradeNextTick(tick, curTick)
				continue
			
			# 触发交易信号，交易开始

			# 开始交易，并返回交易结束时的当前tick
			endTick = self.tradeStart(curTick, signal)
			# 如果返回的tick为空则表示已到数据表末尾
			if endTick is None:
				break
				
			# 返回tick不为空，则继续下一tick
			curTick = self.tradeNextTick(tick, endTick, signal)
		
		# 结束交易，清空仓位
		self.tradeEnd(tick.lastTick(), signal)
		# 执行结束，显示统计信息
		self.cs.show()
	
	# 计算仓位利润
	def __orderProfit (self,
		direction,	#方向
		open,		#开仓价
		price,		#当前价
		):
		orderProfit = 0
		if direction == SIG_TRADE_SHORT:
			orderProfit = open - price
		else:
			orderProfit = price - open
		
		# 单价获利x每单手数x合约乘数
		orderProfit *= self.attrs.numPosToAdd
		orderProfit *= self.attrs.multiplier
		return orderProfit
	
	# 计算浮动利润
	def __floatingProfit (self,
		direction,	#方向
		price,		#当前价
		):
		ret = 0
		poses = self.curPositions()
		for idx in range(poses):
			pos = self.posMgr.getPosition(idx)
			ret += self.__orderProfit(direction, pos.price, price)

		return ret
		
	# 巡航
	def __navigate (self,
		tick,		#交易时间
		price,		#当前价
		direction,	#方向
		):
		# 计算浮动利润
		floatProfit = self.__floatingProfit(direction, price)
		self.debug.dbg("__navigate: %s, price %s, profit %s" % (
						tick, price, floatProfit))
		# 巡航浮动利润，更新数据统计
		self.cs.navigate(tick, floatProfit)
	
	# 返回下一交易时间
	def tradeNextTick (self, 
		tickObj,		#tick接口对象
		tick,			#当前tick
		direction = None,	#方向
		):
		price = self.data.getClose(tick)
		# 如果不在交易中则跳过巡航
		if direction is not None:
			self.__navigate(tick, price, direction)
		
		# 如果不是最后一个tick则要发送并行处理请求，如果是最后一个tick则等待tradeEnd处理
		isLastTick = self.tickSrc.isLastTick(tick)
		if not isLastTick:
			self.__sendParaRequest(tick, ACTION_SKIP, price, 0, direction)
		
		# 继续下一tick
		tickObj.setCurTick(tick)
		# 当前tick已结束，需恢复标志
		self.tagTickParaHandled = False
		return tickObj.getSetNextTick()
	
	# 日志（输出）统一接口
	def log (self, 
		logMsg,	#日志消息
		*args	#参数
		):
		logs = logMsg % (args)
		print logs
	
	