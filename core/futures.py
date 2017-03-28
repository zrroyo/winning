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
import time

from dataMgr.data import Data, DataMink
from ctp.autopos import *
from misc.posmgr import PositionManager
from misc.debug import Debug
from date import Date, Ticks
from tradestat import *
from emulation import *

#期货信号
SIG_TRADE_LONG		= 1
SIG_TRADE_SHORT		= 2

class Attribute:
	def __init__ (self):
		"""
		期货合约（交易）属性
		"""
		self.maxPosAllowed = 0		#最大允许持仓单位数
		self.numPosToAdd = 0		#每加仓单位所代表的手数
		self.priceVariation = 0		#触发加仓条件的价格差
		self.multiplier = 0		#合约乘数
		self.marginRatio = 0.1		#保证金比率

	def set (self, maxPosAllowed, numPosToAdd, priceVariation,
			multiplier, marginRatio):
		"""
		设置交易属性、参数
		:param maxPosAllowed: 最大允许持仓单位数
		:param numPosToAdd: 每加仓单位所代表的手数
		:param priceVariation: 触发加仓条件的价格差
		:param multiplier: 合约乘数
		:param marginRatio: 保证金比率
		:return: None
		"""
		self.maxPosAllowed = maxPosAllowed
		self.numPosToAdd = numPosToAdd
		self.priceVariation = priceVariation
		self.multiplier = multiplier
		self.marginRatio = marginRatio

class Futures:
	def __init__ (self, contract, config, logDir, debug = False):
		"""
		期货交易
		:param contract: 合约名
		:param config: 合约配置解析接口
		:param logDir: 日志目录
		:param debug: 是否调试
		"""
		self.debug = Debug('Futures: %s' % contract, debug)	#调试接口
		self.dbgMode = debug
		self.contract = contract
		self.logDir = logDir
		self.config = config
		self.database = self.config.getDatabase(contract)

		# 根据不同数据级别启用不同主表和交易数据接口
		if self.config.getDataLevel(contract) == 'days':
			self.table = self.config.getDaykTable(contract)
			self.data = Data(contract, config, debug = False)
		elif self.config.getDataLevel(contract) == 'minutes':
			self.table = self.config.getMinkTable(contract)
			self.data = DataMink(contract, config, debug = False)

		self.contractStart = self.config.getContractStart(contract)
		self.contractEnd = self.config.getContractEnd(contract)
		self.attrs = Attribute()	#属性
		# 持仓管理接口
		self.posMgr = None
		# 用于临时目的Tick帮助接口
		self.tickHelper = Ticks(self.database, self.table,
						startTick = self.contractStart,
						endTick = self.contractEnd)

		# 交易结束时间
		self.stopTickTime = None
		# 结束tick被设置说明已合约末尾
		self.stopTick = None

		# 申明统计数据
		self.tickStat = self.tradeStat = self.comStat = None
		# tick统计、交易统计对应表头
		self.tickStatCols = self.trdStatCols = None
		# tick、交易统计数据存储区
		self.tickStatFrame = self.trdStatFrame = None
		# tick数据汇总
		self.tickStatTotal = None
		# tick数据临时存储区
		self.tickStatDict = {}

		# 当前tick是否已经被处理过
		self.tagTickSentReq = False
		# sched请求消息队列
		self.paraMsgQ = None
		# 与sched共享内存
		self.paraCtrl = None
		# 共享内存保护锁
		self.paraLock = None
		# sched同步点工作状态
		self.fakeSpMode = EMUL_SCHED_MODE_NSP
		# REDO_OSP_MP操作中设置该标志，避免再次发送请求。每tick只允许发送一次
		self.tagResuming = False
		# 合约进程id
		self.pid = -1

	def initStatFrame(self, tkCols = [], trdCols = []):
		"""
		初始化统计数据表，合成表头
		:param tkCols: tick统计属性
		:param trdCols: 策略自定义的统计属性，主要用于REDO_OSP_MP时恢复环境
		:return: None
		"""
		self.tickStat = TickStat()
		self.tickStatCols = TICK_STATS + tkCols
		self.tickStatFrame = pd.DataFrame(columns = self.tickStatCols)
		self.tickStatTotal = pd.DataFrame(columns = self.tickStatCols)
		self.tradeStat = TradeStat()
		self.trdStatCols = TRADE_STATS + trdCols
		self.trdStatFrame = pd.DataFrame(columns = self.trdStatCols)
		# 通用统计数据
		self.comStat = CommonStat()

	# ----------------
	# 属性方法
	# ----------------
	
	def setAttrs (self, maxPosAllowed, numPosToAdd, priceVariation):
		"""
		设置外部传入属性
		:param maxPosAllowed: 最大允许持仓单位数
		:param numPosToAdd: 每加仓单位所代表的手数
		:param priceVariation: 触发加仓条件的价格差
		:return: None
		"""
		self.attrs.set(maxPosAllowed = maxPosAllowed,
			       numPosToAdd = numPosToAdd,
			       priceVariation = priceVariation,
			       multiplier = int(self.config.getMultiplier(self.contract)),
			       marginRatio = float(self.config.getMarginRatio(self.contract)),
			       )
		
		# 初始化持仓管理接口
		self.posMgr = PositionManager(maxPosAllowed,
					      prompt = self.contract,
					      debug = False)

	# ----------------
	# 持仓方法
	# ----------------
	
	# 返回当前仓位
	def curPositions (self):
		return self.posMgr.numPositions()
	
	# 清空持仓
	def clearPositions (self):
		return self.posMgr.empty()
	
	def getPosition (self, num = None):
		"""
		返回第num个仓位，num从１开始记
		:param num: 仓位索引
		:return: 索引对应仓位
		"""
		# 默认（num为None）返回最后一个仓位
		if not num:
			num = self.posMgr.numPositions()
			
		return self.posMgr.getPosition(num)

	def __mktime (self, tick):
		"""
		将tick转化成秒数
		:param tick: 交易时间
		:return: tick对应秒数
		"""
		return time.mktime(tick.timetuple())

	def __totick (self, time_sec):
		"""
		将秒数转化成tick
		:param time_sec: 秒数
		:return: 秒数时间对应tick
		"""
		_time = time.localtime(time_sec)
		ret = datetime(_time.tm_year, _time.tm_mon, _time.tm_mday,
			 	_time.tm_hour, _time.tm_min, _time.tm_sec)
		return self.tickHelper.convertToDBtime(ret)

	def __ReqMsg (self, tick, type = EMUL_REQ_INVALID, pos = 0, capital = 0):
		"""
		生成sched请求消息
		:param tick:
		:param type:
		:param pos:
		:param capital:
		:return: 调度请求
		"""
		req = ReqMsg()
		req.mode = self.fakeSpMode
		req.type = type
		req.tick = self.__mktime(tick)
		req.pid = self.pid
		req.pos = pos
		req.capital = capital
		return req

	def __sendParaRequest (self, tick, type, volume, capital, profit = 0):
		"""
		向调度器发出交易请求
		:param tick: 时间
		:param type: 操作类型
		:param volume: 开仓手数
		:param capital: 资金
		:param profit: 影响利润
		:return: 申请成功返回True，否则返回False
		"""
		if not self.paraMsgQ:
			return False

		req = self.__ReqMsg(tick, pos = volume, capital = capital)
		self.debug.dbg("__sendParaRequest: tick %s [%s], type %s, vol %s, "
					"capital %s, profit %s, fakeSpMode %s" %
				(tick, req.tick, type, req.pos, req.capital, profit, req.mode))

		self.paraLock.acquire()
		if self.fakeSpMode != self.paraCtrl.mode:
			# OSP状态发生改变的话请求已无意义
			self.paraLock.release()
			self.debug.dbg("__sendParaRequest: fakeSpMode %s not matching para mode %s" % (
								self.fakeSpMode, self.paraCtrl.mode))
			return False
		elif self.fakeSpMode == EMUL_SCHED_MODE_NSP:
			if type == EMUL_FUT_ACT_OPEN:
				req.type = EMUL_REQ_NSP_OPEN
			elif type == EMUL_FUT_ACT_CLOSE:
				req.type = EMUL_REQ_NSP_CLOSE
		elif self.fakeSpMode == EMUL_SCHED_MODE_OSP:
			if type == EMUL_FUT_ACT_OPEN:
				# 在OSP模式开仓默认为拒绝，如有必要sched进程会发出重置命令
				self.paraLock.release()
				return False
			elif type == EMUL_FUT_ACT_CLOSE:
				req.type = EMUL_REQ_OSP_CLOSE

		# 合约最后tick，OSP进程可能会被重置，需等待sched明确是否可以结束。
		if self.stopTick:
			req.type |= EMUL_REQ_END

		# 已发送过消息，忽略该tick的ack确认信号。
		self.tagTickSentReq = True

		# NP操作仅有NSP.CLOSE，并不会被sched拒绝，所以无需等待
		if req.type & EMUL_REQ_NSP_CLOSE > 0:
			self.paraCtrl.nr_np += 1
			self.paraLock.release()
			self.paraMsgQ.put(req)
			self.debug.dbg("__sendParaRequest: sending req: type %s, nr_np %s" % (
						req.type, self.paraCtrl.nr_np))
			return True

		# WP依赖sched发出命令，进入等待前清除命令，确保不会误判
		self.paraCtrl.command = EMUL_CA_CMD_CLEAR
		self.paraLock.release()

		self.debug.dbg("__sendParaRequest: sending req: type %s, nr_np %s" % (
							req.type, self.paraCtrl.nr_np))

		# WP操作需等待（EMUL_REQ_NSP_OPEN、EMUL_REQ_OSP_CLOSE（|EMUL_REQ_END）
		self.paraMsgQ.put(req)
		allowed = False
		while True:
			self.paraLock.acquire()
			self.debug.dbg("__sendParaRequest: command %s" % self.paraCtrl.command)
			if self.paraCtrl.command == EMUL_CA_CMD_WP_MOVE_ON:
				allowed = True if self.paraCtrl.approve == 1 else False
				self.debug.dbg("__sendParaRequest: WP_MOVE_ON: mode %s, allow %s" % (
									self.paraCtrl.mode, allowed))
				self.paraLock.release()
				break
			elif self.paraCtrl.command == EMUL_CA_CMD_REDO_OSP_MP:
				# OSP.Close被sched识别无效，退出进入__tickParaHandler处理
				self.debug.dbg("__sendParaRequest: REDO_OSP_MP")
				#记录req类型，以便后续辨别发生重置位置
				self.tickStat.reqtype = req.type
				self.paraLock.release()
				break
			elif self.paraCtrl.command == EMUL_CA_CMD_TK_STAT:
				# osp close在等待过程中可能收到sched命令，不响应会造成“死锁”
				self.debug.dbg("__sendParaRequest: TK_STAT")
				self.__schedCmdHandler(self.__mktime(tick))
				self.paraLock.release()
			else:
				self.paraLock.release()
				time.sleep(0.002)
		return allowed

	def openPositions (self, tick, price, direction, volume = 1):
		"""
		开仓处理
		:param tick: 交易时间
		:param price: 成交价
		:param direction: 多空方向
		:param volume: 影响仓数
		:return: 成功返回True，否则返回False
		"""
		# 如果加仓失败返回False
		if not self.posMgr.pushPosition(tick, price, volume, direction):
			return False

		# capital = volume * price * self.attrs.multiplier * self.attrs.marginRatio
		capital = 0

		#
		if not self.tagResuming and \
			not self.__sendParaRequest(tick, EMUL_FUT_ACT_OPEN, volume, capital):
			# 请求失败，需清除误加仓位
			self.posMgr.popPosition()
			#
			self.tickStat.resPos = 1
			self.tickStat.resCap = capital
			self.tickStat.resAct = EMUL_FUT_ACT_OPEN
			return False

		self.log("		-->> Open: %s, poses %s <<--" % (
						price, self.curPositions()))
		return True
	
	def closePositions (self, tick, price, direction, numPos = 1):
		"""
		平仓处理
		:param tick: 交易时间
		:param price: 成交价
		:param direction: 多空方向
		:param numPos: 影响仓数
		:return: 成功返回True，否则返回False
		"""
		# 从第一仓开始按序减仓
		_close = self.posMgr.posStack[:numPos]
		_profitL = [ self.__orderProfit(direction, pos.price, price) for pos in _close ]
		nrClose = len(_profitL)
		# 确认操作是否被允许
		# capital = numPos * price * self.attrs.multiplier * self.attrs.marginRatio
		if not self.__sendParaRequest(tick, EMUL_FUT_ACT_CLOSE, nrClose, 0):
			return False

		# 操作被允许，移除仓位，并更新统计数据
		self.posMgr.posStack = self.posMgr.posStack[numPos:]
		_close = zip(_close, _profitL)
		for (pos, profit) in _close:
			self.log("		<<-- Close: open %s, close %s, profit %s -->>" % (
							pos.price, price, profit))

		# 平仓需统计交易单相关统计数据
		closeProfit = sum(_profitL)
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

		return True

	def __appendTickStatToFrame (self, verified = True):
		"""
		更新tick统计数据区
		:param verified: 数据是否已经袯验证过不需要重置,可以合入总表
		:return: None
		"""
		self.tickStatFrame = self.tickStatFrame.append(
					pd.DataFrame(self.tickStatDict).T)
		# self.debug.dbg("__appendTickStatToFrame: tickStatFrame \n%s" %
		# 	       			self.tickStatFrame[self.tickStatCols])

		if verified:
			self.tickStatTotal = self.tickStatTotal.append(self.tickStatFrame)

	def __clearTickStatFrame (self, tick = None):
		"""
		清空临时存储区、统计区
		:param tick: 交易时间，指定则清空tick及以后数据
		:return: None
		"""
		self.tickStatDict.clear()
		if not tick:
			# 默认清空所有数据
			self.tickStatFrame.drop(self.tickStatFrame.index, inplace = True)
			return

		# 仅移除>=tick的数据
		_start = list(self.tickStatFrame.index).index(tick)
		self.tickStatFrame.drop(self.tickStatFrame[_start:].index, inplace = True)

	def __exitTrade (self, tick):
		"""
		交易结束操作
		:param tick: 结束tick
		:return: None
		"""
		self.__appendTickStatToFrame()
		# self.debug.dbg("__exitTrade: statFrame: \n%s" % self.tickStatFrame)
		# 统计tick数据
		_sum = self.tickStatFrame.sum()
		# self.debug.dbg("__exitTrade: _sum: \n%s" % _sum)
		_floatMov = self.tickStatFrame[TK_FLOAT_MOV].astype(float)
		_floatDesc = _floatMov.describe()
		# self.debug.dbg("__exitTrade: _floatMov %s,\ntype %s, \n_floatDesc: %s" % (
		# 					_floatMov, type(_floatMov), _floatDesc))
		# 统计交易数据
		self.tradeStat.tickEnd = tick
		self.tradeStat.profit = _sum[TK_ORD_PROFIT]
		_floatMov = self.tickStatFrame[TK_FLOAT_MOV]
		self.tradeStat.tickFloatMax = list(_floatMov[_floatMov == _floatDesc['max']].index)[0]
		self.tradeStat.tickFloatMin = list(_floatMov[_floatMov == _floatDesc['min']].index)[0]

		self.log("              ++++++ Business profit %s ++++++" % self.tradeStat.profit)
		self.log("              ****** Total profit %s ******" % self.comStat.cumProfit)

		# 将交易数据插入交易表
		values = self.tradeStat.values(_sum, _floatDesc)
		self.trdStatFrame = self.trdStatFrame.append(
					pd.DataFrame([values], columns = self.trdStatCols),
					ignore_index = True)

		# 清空临时存储区、统计区，准备记录退出后不在交易中的tick数据
		self.__clearTickStatFrame()

	# ----------------
	# 交易方法
	# ----------------

	def signalStartTrading (self, tick):
		"""
		触发开始交易信号
		:param tick: 交易时间
		:return: SIG_TRADE_SHORT、SIG_TRADE_LONG、None
		"""
		return None

	def signalEndTrading (self, tick, direction):
		"""
		触发结束交易信号
		:param tick: 交易时间
		:param direction: 多空方向
		:return: 触发结束信号返回True，否则返回False
		"""
		return False
	
	def signalCutLoss (self, tick, direction):
		"""
		触发止损信号
		:param tick: 交易时间
		:param direction: 多空方向
		:return: 触发止损信号返回True，否则返回False
		"""
		return False
	
	def signalAddPosition (self, tick, direction):
		"""
		触发加仓信号
		:param tick: 交易时间
		:param direction: 多空方向
		:return: 触发加仓信号返回True，否则返回False
		"""
		return False
	
	def signalStopProfit (self, tick, direction):
		"""
		触发止赢信号
		:param tick: 交易时间
		:param direction: 多空方向
		:return: 触发止赢信号返回True，否则返回False
		"""
		return False

	def __signalToDirection (self, signal):
		"""
		交易信号转换成方向字符串
		:param signal: 交易信号
		:return:信号字串
		"""
		if signal == SIG_TRADE_SHORT:
			return 'Short'
		elif signal == SIG_TRADE_LONG:
			return 'Long'
		else:
			return None

	def __validSignal (self, signal):
		"""
		检查是否是有效信号
		:param signal: 信号
		:return: 有效返回True，否则返回False
		"""
		if signal and self.stopTick:
			# 最后一个tick开仓信号无意义
			self.debug.warn("__validSignal: ignore the signal on last tick.")
			return False

		return signal

	def __tradeStart (self, tickSrc, startTick, signal):
		"""
		新交易触发，开始交易
		:param startTick: 开始交易时间
		:param tickSrc: 交易时间接口
		:param signal: 交易信号
		:return: 执行到结尾返回None，否则为交易结束时tick
		"""
		self.debug.dbg("__tradeStart: Start Trading: [%s][%s]" % (
					self.__signalToDirection(signal), startTick))

		# 各交易单独分配数据统计区域
		self.tradeStat = TradeStat()
		self.tradeStat.tickStart = startTick

		if not self.__tradeAddPositions(startTick, signal):
			# 加仓失败，可能是远程sched仓位不足，需确保以当前tick退出
			self.debug.warn("__tradeStart: adding position denied.")
			return startTick

		# 记录退出后不在交易中的tick数据，并且准备开始新交易清空存储区
		self.__appendTickStatToFrame()
		self.__clearTickStatFrame()

		# 得到tick中的下一交易时间
		nextTick = self.__tradeNextTick(tickSrc, signal)

		# 除非到数据表结尾或交易退出，否则一直交易
		while nextTick:
			if self.signalEndTrading(nextTick, signal) or self.stopTick:
				"""
				1）触发退出交易信号；2）到达最后一个tick不允许退出外的任何操作；
				"""
				self.debug.dbg("__tradeStart: End Trading: [%s][%s] stop tick %s" % (
						self.__signalToDirection(signal), nextTick, self.stopTick))
				self.__tradeEnd(nextTick, signal)
				return nextTick
				
			elif self.signalCutLoss(nextTick, signal):
				"""
				止损
				"""
				self.debug.dbg("__tradeStart: Cut Loss: [%s][%s]" % (
							self.__signalToDirection(signal), nextTick))
				self.tradeCutLoss(nextTick, signal)
				# 防止止损操作重载时统计信息遗漏
				self.tickStat.cutLoss = 1
				# 如果止损后仓位为０，说明交易结束，返回当前tick
				if self.curPositions() == 0:
					return nextTick

			elif self.signalAddPosition(nextTick, signal):
				"""
				加仓
				"""
				self.debug.dbg("__tradeStart: Add Position: [%s][%s]" % (
							self.__signalToDirection(signal), nextTick))
				self.__tradeAddPositions(nextTick, signal)

			elif self.signalStopProfit(nextTick, signal):
				"""
				止赢
				"""
				self.debug.dbg("__tradeStart: Stop Profit: [%s][%s]" % (
							self.__signalToDirection(signal), nextTick))
				self.tradeStopProfit(nextTick, signal)
				# 防止止损操作重载时统计信息遗漏
				self.tickStat.stopWin = 1

			nextTick = self.__tradeNextTick(tickSrc, signal)
		
		# 正常结束时不从这返回，因为交易结束要么正常触发结束信号，
		# 要么是最后一个tick(stopTick被设置)。但如果数据表中仅
		# 有一个tick且触发开仓信号则从这里返回
		return None

	def __tradeAddPositions (self, tick, direction):
		"""
		加仓
		:param tick: 交易时间
		:param direction: 方向
		:return: 成功返回True，否则返回False
		"""
		price = self.data.getClose(tick)
		volume = self.attrs.numPosToAdd
		
		self.debug.dbg("__tradeAddPositions: tick %s, price %s, volume %s, direction %s" % (
						tick, price, volume, direction))

		# 开仓
		if self.openPositions(tick, price, direction, volume):
			self.tickStat.addPos = 1
			return True

		return False

	def tradeCutLoss (self, tick, direction):
		"""
		止损。必须被重载实现
		@MUST_OVERRIDE
		:param tick: 交易时间
		:param direction: 方向
		:return: 成功返回True，否则返回False
		"""
		return False
	
	def tradeStopProfit (self, tick, direction):
		"""
		止赢。必须被重载实现
		@MUST_OVERRIDE
		:param tick: 交易时间
		:param direction: 方向
		:return: 成功返回True，否则返回False
		"""
		return False
	
	def __tradeEnd (self, tick, direction):
		"""
		交易结束处理
		:param tick: 交易时间
		:param direction: 方向
		:return: None
		"""
		# 交易结束平掉所有仓位
		price = self.data.getClose(tick)
		self.closePositions(tick, price, direction, self.curPositions())

	def tradeStoreTickEnv (self):
		"""
		追加需在tickStatFrame记录的数据，私有变量、统计数据等
		:return: 数据列表
		"""
		return []

	def tradeResumeTickEnv (self, values):
		"""
		从tickStatFrame中数据恢复执行环境
		:param values: 待恢复的数据，dict类型
		:return: None
		"""
		pass

	def __getRealStartAndEndTick (self, startTick = None, stopTick = None,
					follow = False):
		"""
		估计实际的开始和结束时间
		:param startTick: 开始tick。支持字符时间、秒数时间
		:param stopTick: 结束tick
		:param follow: 跳过startTick，从下一tick开始
		:return: 真实的开始、结束tick
		"""
		# 默认从第一个tick开始
		retStart = self.tickHelper.firstTick()

		if startTick:
			if isinstance(startTick, float):
				# 传入时间可能是秒数，先做转化
				startTick = self.__totick(startTick)
			elif isinstance(startTick, str):
				# 字符时间转化为数据库时间
				startTick = self.tickHelper.strToDateTime(startTick)

			self.debug.dbg("__getRealStartAndEndTick: startTick type %s, "
				       "converted to %s" % (type(startTick), startTick))

			# 指定的交易时间不一定存在，如不存在则用下一个最接近的tick开始
			retStart = self.tickHelper.getNextNearTick(startTick, 1)
			if follow:
				# follow为假从指定的最近时间开始，否则紧接startTick执行
				retStart = self.tickHelper.getNexNumTick(startTick, 1)

		# 默认为最后一个tick结束
		retStop = None
		if stopTick:
			# 如指定结束时间则从指定tick（时间存在）或之前最接近的tick结束（时间不存在）
			retStop = self.tickHelper.strToDateTime(stopTick)
			if self.config.getDataLevel(self.contract) == 'minutes':
				# 指定时间为日期，分钟级数据需要设置结束时间
				retStop = datetime(retStop.year, retStop.month, retStop.day, 15, 0, 0)

		return retStart,retStop

	def __exit (self):
		"""
		即将退出合约进程，将交易、tick数据导出保存。
		:return: None
		"""
		# 将交易数据以excel格式保存
		self.debug.dbg("__exit: trdStatFrame: \n%s" % self.trdStatFrame.T)
		_trdXlsx = "%s/%s_TRADE_STAT.xlsx" % (self.logDir, self.contract)
		self.trdStatFrame.T.to_excel(_trdXlsx, float_format = "%.2f")

		# 部分tick不在交易中，没有机会存入存储区
		self.__appendTickStatToFrame()
		# 将tick数据以excel格式保存
		_data = "%s/%s" % (self.logDir, self.contract)
		self.tickStatTotal[self.tickStatCols].to_excel("%s_TICK_STAT.xlsx" % _data,
								float_format = "%.2f")
		self.__clearTickStatFrame()

	def start (self, startTick = None, stopTick = None, msgQ = None,
			shmem = None, shmlock = None, storeLog = False, follow = False):
		"""
		启动交易入口
		:param startTick: 开始交易时间。支持秒数时间、字符串时间如（2013-10-15）
		:param stopTick: 结束交易时间，字符串时间如（2013-12-31）
		:param msgQ: sched请求消息队列
		:param shmem: 与sched共享内存
		:param shmlock: 共享内存保护锁
		:param storeLog: 保存合约日志
		:param follow: 从startTick后一tick开始执行
		:return: None
		"""
		# import cProfile
		# cp = cProfile.Profile()
		# cp.clear()
		# cp.enable()

		self.debug.info("start: startTick %s, stopTick %s" % (startTick, stopTick))

		self.pid = os.getpid()

		if storeLog:
			# 保存日志
			_logName = "%s/%s" % (self.logDir, self.contract)
			fd = open(_logName, "w")
			sys.stdout = sys.stderr = fd

		self.paraMsgQ = msgQ
		self.paraCtrl = shmem
		self.paraLock = shmlock

		tickSrc = Ticks(self.database, self.table, self.contractStart, self.contractEnd)
		curTick,self.stopTickTime = self.__getRealStartAndEndTick(startTick, stopTick, follow)
		tickSrc.setCurTick(curTick)

		self.debug.dbg("start: start %s at %s, stop tick %s" % (
					self.contract, curTick, self.stopTickTime))

		while curTick:
			endTick = None
			# 检测是否触发交易信号
			signal = self.signalStartTrading(curTick)
			# self.debug.dbg("signal: %s" % signal)
			if not self.__validSignal(signal):
				curTick = self.__tradeNextTick(tickSrc)
				continue
			
			# 触发信号，开始交易
			endTick = self.__tradeStart(tickSrc, curTick, signal)
			if not endTick:
				# 原则上交易退出时不为None，但数据表中仅有一个tick时会出现
				self.debug.warn("start: found unexpected endTick.")
				break

			# 从返回tick的下一tick继续交易
			curTick = self.__tradeNextTick(tickSrc, signal)

		# 结束时未在交易中，清仓发送EMUL_REQ_END
		if not endTick:
			self.__tradeEnd(self.stopTick, signal)

		# 退出前处理
		self.__exit()
		# cp.disable()
		# cp.print_stats(sort='cumtime')

	def __orderProfit (self, direction, open, price):
		"""
		计算仓位利润
		:param direction: 多空方向
		:param open: 开仓价
		:param price: 当前价
		:return: 单仓利润
		"""
		orderProfit = price - open
		if direction == SIG_TRADE_SHORT:
			orderProfit = open - price

		# 单价获利 * 每单手数 * 合约乘数
		orderProfit *= self.attrs.numPosToAdd * self.attrs.multiplier
		return orderProfit

	def __curPosFloatProfit (self, direction, price):
		"""
		计算当前持仓浮动利润
		:param direction: 方向
		:param price: 当前价
		:return: 持仓浮动利润
		"""
		ret = 0
		# 对当前所有仓位价格求和，以快速求出浮动利润
		_sumPrice = self.posMgr.valueSum(value = 'price')
		if direction == SIG_TRADE_SHORT:
			ret = _sumPrice - price * self.posMgr.numPositions()
		elif direction == SIG_TRADE_LONG:
			ret = price * self.posMgr.numPositions() - _sumPrice

		ret *= self.attrs.numPosToAdd * self.attrs.multiplier
		return ret

	def __floatingProfit (self, direction, price):
		"""
		计算浮动利润
		:param direction: 方向
		:param price: 当前价
		:return: 浮动利润
		"""
		# 当前持仓浮动利润
		ret = self.__curPosFloatProfit(direction, price)
		self.debug.dbg("__floatingProfit: position float %s, cumulate %s, order profit %s" %
			       (ret, self.tradeStat.cumFloat, self.tickStat.orderProfit))
		# 当前浮动赢利=累积利润+当前tick持仓利润+当前tick的交易单利润
		ret += self.tickStat.orderProfit + self.tradeStat.cumFloat
		return ret

	def __storeTickStat (self, tick, price,	direction):
		"""
		保存tick统计数据
		:param tick: 当前tick
		:param price: 当前价格
		:param direction: 多空方向
		:return: None
		"""
		# 当前持仓浮动利润
		_posFloat = self.__curPosFloatProfit(direction, price)
		# 更新当前tick的统计数据
		self.tickStat.floatProPos = _posFloat
		self.tickStat.floatProCum = self.tradeStat.cumFloat
		self.tickStat.floatProfit = self.tickStat.floatProCum + self.tickStat.orderProfit + _posFloat
		# REDO_OSP_MP恢复执行环境时依赖各tick保存策略自定义的数据，如变量等
		values = self.tickStat.values() + self.tradeStoreTickEnv()
		# 交易单利润需累加，以使下一tick计算浮动赢利
		self.tradeStat.cumFloat += self.tickStat.orderProfit
		self.debug.dbg("__storeTickStat: tick %s, price %s, move %s, pos %s, cum %s, order profit %s" %
						(tick, price, self.tickStat.floatProfit, _posFloat,
						 self.tradeStat.cumFloat, self.tickStat.orderProfit))
		# 加快存储速度，先存入字典，再统一追加到tickStatFrame
		self.tickStatDict[tick] = dict(zip(self.tickStatCols, values))

	def __getOpenStat(self, tick, next = False):
		"""
		获取tick附近的开仓数据。
		:param tick: 交易时间
		:param next: False：tick之前；True：tick之后
		:return: 交易tick、仓位、资金、操作
		"""
		try:
			# self.debug.dbg("__getOpenStat: tick %s, tickStatFrame %s" % (
			# 				tick, self.tickStatFrame))
			_tf = self.tickStatFrame[self.tickStatFrame[TK_RES_ACT] == EMUL_FUT_ACT_OPEN]
			# self.debug.dbg("__getOpenStat: tick %s, _tf:1 %s" % (tick, _tf))
			if next:
				_tf = _tf[pd.Series(_tf.index > tick, index = _tf.index)]
				_values = _tf.head(1)[[TK_RES_POS, TK_RES_CAP, TK_RES_ACT]]
			else:
				_tf = _tf[pd.Series(_tf.index <= tick, index = _tf.index)]
				_values = _tf.tail(1)[[TK_RES_POS, TK_RES_CAP, TK_RES_ACT]]

			# self.debug.dbg("__getOpenStat: tick %s, _tf: %s, _values %s" % (
			# 					tick, _tf, _values))

			(pos, capital, action) = tuple(_values.values.tolist()[0])
			_tick = _values.index[0]
		except IndexError:
			return None, 0, 0, MEUL_FUT_ACT_SKIP

		return _tick, int(pos), capital, int(action)

	def __tickEnvResume (self, tickObj, tick):
		"""
		将执行环境恢复到交易中的指定tick点，重新执行
		:param tickObj: tick源
		:param tick: 需恢复到的tick点
		:return: None
		"""
		values = self.tickStatFrame.xs(tick)
		self.debug.dbg("__tickEnvResume: resume to %s, values \n%s" % (tick, values))
		self.tradeResumeTickEnv(values)

		# 丢弃当前的统计数据
		self.tickStat = TickStat()

	def __schedCmdHandler(self, tick, tickObj = None):
		"""
		调度命令响应
		:param tick: 当前tick（秒数）
		:param tickObj: tick源
		:return: 无需重置返回None，否则返回重置tick
		"""
		if self.paraCtrl.command == EMUL_CA_CMD_WP_MOVE_ON:
			# WP操作之后状态可能会有改变
			self.fakeSpMode = self.paraCtrl.mode
			self.paraCtrl.command = EMUL_CA_CMD_CLEAR
			self.debug.dbg("__schedCmdHandler: WP_MOVE_ON: fakeSpMode %s" % self.fakeSpMode)

		elif self.paraCtrl.command == EMUL_CA_CMD_TK_STAT and \
				tick >= self.paraCtrl.tick:
			"""
			sched发出返回tick信息请求
			"""
			# 将数据合入tickStatFrame以方便查询，但可能被重置所以暂不合入总表
			self.__appendTickStatToFrame(verified = False)
			(_tick, self.paraCtrl.pos, self.paraCtrl.capital, self.paraCtrl.action)\
				= self.__getOpenStat(self.__totick(self.paraCtrl.tick))
			self.paraCtrl.tick = self.__mktime(_tick)
			self.paraCtrl.command = EMUL_CA_CMD_CLEAR
			self.debug.dbg("__schedCmdHandler: TK_STAT: tick %s, pos %s, capital %s, action %s" % (
					_tick, self.paraCtrl.pos, self.paraCtrl.capital, self.paraCtrl.action))
			# 数据已追加至tickStatFrame，清空缓存避免重复合入
			self.tickStatDict.clear()

		elif self.paraCtrl.command == EMUL_CA_CMD_REDO_OSP_MP:
			"""
			sched发出重置OSP MP操作请求
			"""
			_tick = self.__totick(self.paraCtrl.tick)
			# 重置之后操作状态明确，需切换为NSP状态
			self.fakeSpMode = EMUL_SCHED_MODE_NSP
			self.debug.dbg("__schedCmdHandler: REDO_OSP_MP: fakeSpMode %s" % self.fakeSpMode)

			if self.paraCtrl.redo_next:
				# 重置@_tick后下一个开仓tick
				# 清除标志避免影响下次重置
				self.paraCtrl.redo_next = 0
				# 将数据合入tickStatFrame以方便查询，但可能被重置所以暂不合入总表
				self.__appendTickStatToFrame(verified = False)
				res = self.__getOpenStat(_tick, True)
				# 数据已追加至tickStatFrame，清空缓存避免重复合入
				self.tickStatDict.clear()
				_inOspWp = self.tickStat.reqtype & EMUL_REQ_OSP_CLOSE
				self.debug.dbg("__schedCmdHandler: reqtype %s, res[0] %s" % (
								self.tickStat.reqtype, res[0]))
				if res[0]:
					# （_tick <= t <= tick）期间有OSP.open发生
					_tick = res[0]
				else:
					# 虽然（_tick <= t <= tick）期间没有OSP.open发生，但
					# 有可能合约已在OSP.WP等待中。如果在则需要重置为NSP.NP，
					# 反之则不用做任何事情
					if not _inOspWp:
						# sched.tick至当前tick间无OSP.Open和OSP.WP发生
						self.paraCtrl.command = EMUL_CA_CMD_CLEAR
						return None

					# 当前tick在OSP.WP，需重置为NSP.Close
					_tick = self.__totick(tick)
			else:
				# sched.tick有OSP.Open需重置，但sched
				# 已处理过该tick，不能再重复发送req
				self.tagResuming = True

			# self.debug.dbg("__schedCmdHandler: tickStatFrame \n%s" % self.tickStatFrame)
			# 先回退current，确保sched不会立即进入下一tick
			prev = tickObj.getPrevNumTick(_tick, 1)
			self.paraCtrl.current = self.__mktime(prev)
			# 同步给sched立即恢复执行
			self.paraCtrl.command = EMUL_CA_CMD_CLEAR
			self.debug.dbg("__schedCmdHandler: redo tick %s, prev %s, set current to %s" % (
								_tick, prev, self.paraCtrl.current))
			# 恢复环境需要消耗时间，放在清除command后提高sched处理效率
			self.__tickEnvResume(tickObj, prev)
			# 重置后缓存中_tick及之后的数据已无效
			self.__clearTickStatFrame(_tick)
			return _tick

		return None

	def __tickParaHandler (self, tickObj, tick):
		"""
		tick并行事件响应
		:param tickObj: tick源
		:param tick: 当前tick
		:return: 无需重置返回None，否则返回重置tick
		"""
		if not self.paraMsgQ:
			return None

		_tick = self.__mktime(tick)
		self.paraLock.acquire()
		redo = self.__schedCmdHandler(_tick, tickObj)
		if redo:
			self.paraLock.release()
			return redo

		# 确保在tick结束时sched发出的ACK请求得到响应
		if self.paraCtrl.ack and _tick >= self.paraCtrl.ack:
			# 如果tick内已发过请求则不需要ack确认
			if not self.tagTickSentReq:
				req = self.__ReqMsg(tick, EMUL_REQ_ACK)
				self.debug.dbg("__tickParaHandler: sending ack")
				self.paraMsgQ.put(req)
			# 清除ack标志避免重复响应
			self.paraCtrl.ack = 0

		# self.debug.dbg("__tickParaHandler: ack %s" % self.paraCtrl.ack)

		# 以便sched读取到前tick信息
		self.paraCtrl.current = _tick
		self.paraLock.release()
		#
		self.tagTickSentReq = False
		self.tagResuming = False
		return None

	def __tradeNextTick (self, tickObj, direction = None):
		"""
		返回下一交易时间
		:param tickObj: tick接口对象
		:param direction: 多空方向
		:return: 下一tick
		"""
		tick = tickObj.curTick()
		price = self.data.getClose(tick)
		# 保存tick统计数据
		self.__storeTickStat(tick, price, direction)

		# 确保交易中的sched命令得到响应
		redo = self.__tickParaHandler(tickObj, tick)
		if redo:
			# 被sched重置到特定tick，跳转执行
			self.debug.info("__tradeNextTick: jump to tick %s" % redo)
			tickObj.setCurTick(redo)
			return redo

		# 该tick完成本次交易结束，清尾
		if self.tickStat.tagTradeEnd:
			self.__exitTrade(tick)
		# 确保各tick数据不会互相干扰，分配新数据存储区
		self.tickStat = TickStat()

		# 继续下一tick
		nextTick = tickObj.getSetNextTick()
		_nxtNxtTick = tickObj.nextTick()
		self.debug.dbg("__tradeNextTick: tick %s, nextTick %s" % (tick, nextTick))

		if self.stopTick:
			# 最后tick执行完成
			return None
		elif not _nxtNxtTick or self.stopTickTime and \
				_nxtNxtTick > self.stopTickTime:
			# 马上进入最后tick
			self.stopTick = nextTick

		return nextTick

	def log (self, logMsg, *args):
		"""
		日志统一打印接口
		:param logMsg: 日志消息
		:param args: 参数
		"""
		logs = "<%s>| %s" % ("{:^12s}".format(self.contract), logMsg % args)
		print logs
