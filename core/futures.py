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
import pandas as pd

from dataMgr.data import *
from ctp.autopos import *
from misc.posmgr import *
from misc.debug import *
from date import *
from attribute import *
from signal import *
from parallel import *
from tradestat import *

# 期货类
class Futures:
	def __init__ (self, 
		contract, 	#合约
		config,		#合约配置解析接口
		debug = False,	#是否调试
		):
		self.dbgMode = debug
		self.contract = contract
		self.config = config
		self.database = self.config.getDatabase(contract)
		self.table = self.config.getMainTable(contract)
		self.contractStart = self.config.getContractStart(contract)
		self.contractEnd = self.config.getContractEnd(contract)
		self.attrs = Attribute()	#属性
		# 持仓管理接口
		self.posMgr = None
		self.debug = Debug('Futures: %s' % contract, debug)	#调试接口
		self.data = Data(contract, config, debug = False)	#数据接口
		# 用于临时目的Tick帮助接口
		self.tickHelper = Ticks(self.database, self.table,
						startTick = self.contractStart,
						endTick = self.contractEnd)
		# 当前tick是否已经被处理过
		self.tagTickParaHandled = False

		# 交易结束时间
		self.stopTickTime = None
		# 指定的交易结束时间并不一定有对应tick，所以需记录实际结束tick
		self.stopTick = None

		# 初始化tick、交易统计表
		self.tickStat = TickStat()
		self.tickStatFrame = pd.DataFrame(columns = TICK_STATS)
		self.tradeStat = TradeStat()
		self.trdStatFrame = pd.DataFrame(columns = TRADE_STATS)
		# 通用数据统计区域
		self.comStat = CommonStat()


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
		self.posMgr = PositionManager(maxPosAllowed,
					      prompt = self.contract,
					      debug = False)

		# 如果使能了并行模拟，则需要为合约初始化
		self.paraCore = paraCore
	
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
		# 确保每一tick只发送一次请求
		if not self.paraCore or self.tagTickParaHandled:
			return True
		
		# 标记该tick已发送过请求
		self.tagTickParaHandled = True
		# 计算浮动利润
		floatProfit = self.__floatingProfit(direction, price)
		isLastTick = True if self.stopTick else False

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
		if not self.__sendParaRequest(tick, ACTION_OPEN, price, 1, direction):
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
		_profitL = []
		for i in range(numPos):
			# 移除仓位并计算利润
			pos = self.posMgr.popPosition(1)
			orderProfit = self.__orderProfit(direction, pos.price, price)
			_profitL.append(orderProfit)
			self.log("		<<-- Close: open %s, close %s, profit %s -->>" % (
							pos.price, price, orderProfit))

		# 平仓需统计交易单相关统计数据
		closeProfit = sum(_profitL)
		nrClose = len(_profitL)
		_profitL = pd.Series(_profitL)
		self.tickStat.ordWins = len(_profitL[_profitL > 0])
		self.tickStat.ordLoses = len(_profitL[_profitL < 0])
		self.tickStat.ordFlat = len(_profitL[_profitL == 0])
		self.tickStat.orderProfit = closeProfit
		# 更新累积交易利润
		self.comStat.cumProfit += closeProfit

		# 如果平仓后仓位为０说明本次交易结束。打印统计信息并重置。
		if self.curPositions() == 0:
			self.tickStat.tagTradeEnd = True

		# 发送并行处理请求
		self.__sendParaRequest(tick, ACTION_CLOSE, price, nrClose, direction, closeProfit)
		return True

	# 交易结束操作
	def __exitTrade (self,
		tick,	#结束tick
		):
		self.debug.dbg("statFrame: \n%s" % self.tickStatFrame)
		# 统计tick数据
		_sum = self.tickStatFrame.sum()
		self.debug.dbg("_sum: \n%s" % _sum)
		_floatBuf = self.tickStatFrame[TK_FLOAT_MOV]
		_floatDesc = _floatBuf.describe()
		self.debug.dbg("_floatDesc: \n%s" % _floatDesc)
		# 统计交易数据
		self.tradeStat.tickEnd = tick
		self.tradeStat.profit = _sum[TK_ORD_PROFIT]
		_floatBuf = self.tickStatFrame[TK_FLOAT_MOV]
		self.tradeStat.tickFloatMax = list(_floatBuf[_floatBuf == _floatDesc['max']].index)[0]
		self.tradeStat.tickFloatMin = list(_floatBuf[_floatBuf == _floatDesc['min']].index)[0]

		self.log("              ++++++ Business profit %s ++++++" % self.tradeStat.profit)
		self.log("              ****** Total profit %s ******" % self.comStat.cumProfit)

		# 将交易数据插入交易表
		values = self.tradeStat.values(_sum, _floatDesc)
		self.trdStatFrame = self.trdStatFrame.append(
					pd.DataFrame([values], columns = TRADE_STATS),
					ignore_index = True)
		# 交易数据依赖tick统计表，交易完成需清空
		self.tickStatFrame.drop(self.tickStatFrame.index, inplace = True)
		self.debug.dbg("trdStatFrame: \n%s" % self.trdStatFrame.T)

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
		signal,		#交易信号（方向）
		):
		self.debug.dbg("tradeStart: Start Trading: [%s][%s]" % (
					self.__signalToDirection(signal), startTick))

		# 各交易单独分配数据统计区域
		self.tradeStat = TradeStat()
		self.tradeStat.tickStart = startTick

		# 使用独立交易时间管理接口，保持独立性，避免互相影响。
		tickSrc = Ticks(self.database, self.table,
					startTick = self.contractStart,
					endTick = self.contractEnd)
		tickSrc.setCurTick(startTick)
		# 交易信号已经触发，先入仓
		self.tradeAddPositions(startTick, signal)
		# 得到tick中的下一交易时间
		nextTick = self.tradeNextTick(tickSrc, startTick, signal)

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
				#
				self.tickStat.cutLoss = 1
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
				#
				self.tickStat.stopWin = 1

			# 下一tick继续
			nextTick = self.tradeNextTick(tickSrc, nextTick, signal)
		
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
		if self.openPositions(tick, price, direction, volume):
			self.tickStat.addPos = 1

	# 止损
	def tradeCutLoss (self,
		tick,		#交易时间
		direction,	#方向
		):
		"""
		必须被重载实现
		@MUST_OVERRIDE
		"""
		return
	
	# 止赢
	def tradeStopProfit (self,
		tick,		#交易时间
		direction,	#方向
		):
		"""
		必须被重载实现
		@MUST_OVERRIDE
		"""
		return
	
	# 交易结束处理
	def tradeEnd (self,
		tick,		#交易时间
		direction,	#方向
		):
		#停止交易，清空所有仓位
		self.closePositions(tick = tick, 
				price = self.data.getClose(tick), 
				direction = direction, 
				numPos = self.curPositions())

	# 估计实际的开始和结束时间
	def __getRealStartAndEndTick (self,
		startTick = None,
		stopTick = None,
		):
		retStart = self.tickHelper.firstTick()
		# 指定的交易时间不一定存在，如不存在则用下一个最接近的tick开始
		if startTick:
			retStart = self.tickHelper.getNextNearTick(startTick, 1)

		retStop = None
		# 默认为最后一个tick，如指定则为指定tick或之前最接近的一个tick
		if stopTick:
			retStop = Date.strToDateTime(stopTick)

		return retStart,retStop

	# 开始交易
	def start (self,
		startTick = None,	#开始交易时间
		stopTick = None,	#
		):
		tickSrc = Ticks(self.database, self.table,
					startTick = self.contractStart,
					endTick = self.contractEnd)
		curTick,self.stopTickTime = self.__getRealStartAndEndTick(startTick, stopTick)

		self.debug.dbg("start %s at %s, stop tick %s" % (
					self.contract, curTick, self.stopTickTime))

		while curTick is not None:
			# 检测是否触发交易信号
			signal = self.signalStartTrading(curTick)
			if not self.__validStartSignal(signal):
				curTick = self.tradeNextTick(tickSrc, curTick)
				continue
			
			# 触发信号，开始交易
			endTick = self.tradeStart(curTick, signal)
			# 从返回tick的下一tick继续交易
			curTick = self.tradeNextTick(tickSrc, endTick, signal)
		
		# 结束交易，清空仓位
		self.tradeEnd(self.stopTick, signal)

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
		orderProfit *= self.attrs.numPosToAdd * self.attrs.multiplier
		return orderProfit

	# 当前持仓浮动利润
	def __curPosFloatProfit (self,
		direction,	#方向
		price,		#当前价
		):
		ret = 0
		# 对当前所有仓位价格求和，以快速求出浮动利润
		_sumPrice = self.posMgr.valueSum(value = 'price')
		if direction == SIG_TRADE_SHORT:
			ret = _sumPrice - price * self.posMgr.numPositions()
		elif direction == SIG_TRADE_LONG:
			ret = price * self.posMgr.numPositions() - _sumPrice

		ret *= self.attrs.numPosToAdd * self.attrs.multiplier
		return ret

	# 计算浮动利润
	def __floatingProfit (self,
		direction,	#方向
		price,		#当前价
		):
		# 当前持仓浮动利润
		ret = self.__curPosFloatProfit(direction, price)
		self.debug.dbg("__floatingProfit: position float %s, cumulate %s, order profit %s" %
			       (ret, self.tradeStat.cumFloat, self.tickStat.orderProfit))
		# 当前浮动赢利=累积利润+当前tick持仓利润+当前tick的交易单利润
		ret += self.tickStat.orderProfit + self.tradeStat.cumFloat
		return ret

	# 存储tick的统计数据
	def __storeTickStat (self,
		tick,		#交易时间
		price,		#当前价
		direction,	#方向
		):
		# 当前持仓浮动利润
		_posFloat = self.__curPosFloatProfit(direction, price)
		# 更新当前tick的统计数据
		self.tickStat.floatProPos = _posFloat
		self.tickStat.floatProCum = self.tradeStat.cumFloat
		self.tickStat.floatProfit = self.tickStat.floatProCum + self.tickStat.orderProfit + _posFloat
		values = self.tickStat.values()
		# 交易单利润需累加，以使下一tick计算浮动赢利
		self.tradeStat.cumFloat += self.tickStat.orderProfit
		self.debug.dbg("__storeTickStat: tick %s, price %s, move %s, pos %s, cum %s, order profit %s" %
						(tick, price, self.tickStat.floatProfit, _posFloat,
						 self.tradeStat.cumFloat, self.tickStat.orderProfit))
		# 将tick数据存入数据表
		self.tickStatFrame = self.tickStatFrame.append(
					pd.DataFrame([values], columns = TICK_STATS, index = [tick])
					)

		# self.debug.dbg("statFrame: %s" % self.tickStatFrame)

	# 返回下一交易时间
	def tradeNextTick (self, 
		tickObj,		#tick接口对象
		tick,			#当前tick
		direction = None,	#方向
		):
		if not tick:
			return None

		price = self.data.getClose(tick)
		# 如不在交易中无需更新持仓变化
		if direction is not None:
			self.__storeTickStat(tick, price, direction)

		# 交易的最后一tick
		if self.tickStat.tagTradeEnd:
			self.__exitTrade(tick)
		# 为了各tick统计数据隔离，重新分配数据存储区
		self.tickStat = TickStat()

		# 继续下一tick
		tickObj.setCurTick(tick)
		nextTick = tickObj.getSetNextTick()
		self.debug.info("tradeNextTick: tick %s, nextTick %s" % (tick, nextTick))

		try:
			# 如果指定的交易结束时间到或为最后tick，则交易结束
			if self.stopTickTime and nextTick > self.stopTickTime \
				or tickObj.isLastTick(tick):
				# 提醒tradeEnd统一平仓，并发出信号请求同步，释放仓位
				self.stopTick = tick
				# 之前可能已发出过并行处理请求，清除标志以便最终能发出结束请求
				self.tagTickParaHandled = False
				self.debug.info("reach the stop tick %s" % self.stopTick)
				return None
			else:
				self.__sendParaRequest(tick, ACTION_SKIP, price, 0, direction)

			# 新tick产生，标志复位
			self.tagTickParaHandled = False

		except TypeError, e:
			self.debug.error("tradeNextTick: found error %s" % e)
			self.stopTick = tick
			# 已到表尾，交易结束，但之前可能已发出过并行处理请求，清除标志以便最终能发出结束请求
			self.tagTickParaHandled = False
			return None

		return nextTick
	
	# 日志（输出）统一接口
	def log (self, 
		logMsg,	#日志消息
		*args	#参数
		):
		logs = "<%s>| %s" % ("{:^12s}".format(self.contract), logMsg % args)
		print logs
	
	