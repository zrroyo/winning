#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2015年 07月 05日 星期日 18:02:02 CST

并行执行模块
"""

import sys
sys.path.append("..")
import thread
import time

from misc.debug import Debug
from statistics import *

# 操作类型
ACTION_OPEN	= "OPEN"
ACTION_CLOSE	= "CLOSE"
ACTION_SKIP	= "SKIP"
# 需要阻塞的action类型
BLOCKED_ACTION_TYPES = [ACTION_OPEN, ACTION_CLOSE]

# ParaCore（巡航时）默认合约名
DEF_CONTRACT	= "ParaCore"

# 操作记录
class Action:
	def __init__ (self,
		contract,	#合约
		tick,		#时间
		type,		#操作类型
		price,		#价格
		volume,		#开仓手数
		direction,	#方向
		floatProfit,	#浮动利润
		closeProfit,	#平仓利润
		isLastTick,	#
		):
		self.contract = contract
		self.tick = tick
		self.type = type
		self.price = price
		self.volume = volume
		self.direction = direction
		self.floatProfit = floatProfit
		self.closeProfit = closeProfit
		self.isLastTick = isLastTick

# 操作记录队列
class ActionQueue:
	def __init__ (self,
		debug = False,	#是否调试
		):
		self.debug = Debug('ActionQueue', debug)	#调试接口
		# 操作记录队列
		self.actQueue = []
		# 保护锁
		self.lock = thread.allocate_lock()
		# 同步窗口内的操作已就绪
		self.readyToSelect = False
		# 遇到需阻塞的操作请求
		self.reqBlocked = False
		# 已遇到最后一个操作记录，预示合约结束
		self.onLastTick = False
	
	# 将请求压入操作队列
	def push (self,
		contract,	#合约
		tick,		#时间
		type,		#操作类型
		price,		#价格
		volume,		#开仓手数
		direction,	#方向
		floatProfit,	#浮动利润
		closeProfit,	#平仓利润
		isLastTick,	#是否是最后一个tick
		):
		act = Action(tick = tick, 
				type = type, 
				price = price, 
				volume = volume, 
				direction = direction, 
				floatProfit = floatProfit, 
				closeProfit = closeProfit,
				contract = contract,
				isLastTick = isLastTick,
				)
		self.lock.acquire()
		self.actQueue.append(act)
		self.debug.dbg("push: %s: tick %s, type %s, price %s" % (
					contract, tick, type, price))

		self.lock.release()

	# 得到操作队列的头元素
	def popHead (self):
		try:
			return self.actQueue.pop(0)
		except IndexError:
			return None

# 操作管理接口，每个合约都需要分配一个单独操作管理接口
class ActionManager:
	def __init__ (self):
		self.actQueue = None	#操作记录队列接口
		self.prevAction = None	#上一个操作记录
		
		# 阻塞锁，有阻塞请求时阻塞合约线程
		self.blockLock = thread.allocate_lock()
		# 允许开仓
		self.allowOpen = False
		# 通知已接受标志
		self.tagNotifyRecved = False

# 加仓管理接口
class PositionAddManager:
	def __init__ (self,
		maxAllowed,	#最大允许仓位
		debug = False,	#是否调试
		):
		self.debug = Debug('PositionAddManager', debug)	#调试接口
		self.maxAllowed = maxAllowed
		self.available = maxAllowed	#剩余仓位
	
	# 分配仓位
	def alloc (self,
		action,	#操作记录
		):
		# 如果申请数大于剩余数则失败
		if action.volume > self.available:
			self.debug.error("alloc: denied, maxAllowed %s, available %s, request %s" % (
							self.maxAllowed, self.available, action.volume))
			return False
		
		self.available -= action.volume
		return True
	
	# 释放仓位
	def free (self,
		action,	#操作记录
		):
		if self.available + action.volume > self.maxAllowed:
			self.debug.error("free: denied, available %s request %s overflows maxAllowed %s" % (
							self.available, action.volume, self.maxAllowed))
			return False

		self.available += action.volume
		return True
	
	# 返回当前的仓位
	def curPos (self):
		return self.maxAllowed - self.available
		

# 并行测试、执行控制核心
class ParallelCore:
	def __init__ (self,
		config,		#配置文件接口
		dumpName,	#统计信息Dump名
		debug = False,	#是否调试
		):
		self.debug = Debug('ParallelCore', debug)	#调试接口
		self.dbgMode = debug
		self.config = config

		# 操作管理队列
		self.actionManagers = {}
		# 工作队列，从各合约中选取action
		self.workQueue = []
		#记录工作队列中上一action的tick
		self.prevTick = None

		# 并行数控制合约如期并行执行。每启动一个活动线程并行数加１，退出则减１。
		self.mgrLock = thread.allocate_lock()
		self.parallelLevel = int(self.config.getParallelLevel())	#最大允许并行数
		self.curParallelLevel = 0	# 当前并行数

		# 仓位管理接口
		self.posMgr = PositionAddManager(
				maxAllowed = int(self.config.getParallelAddMaxAllowed()),
				debug = debug)
		# 利润统计接口
		self.profitStat = ProfitStat(dumpName, debug)
	
	# 分配操作管理接口
	def allocManager (self,
		contract,	#合约
		):
		self.mgrLock.acquire()
		if self.curParallelLevel >= self.parallelLevel:
			self.mgrLock.release()
			return False

		actMgr = ActionManager()
		actMgr.actQueue = ActionQueue(self.dbgMode)
		self.actionManagers[contract] = actMgr
		#占住阻塞锁以保证合约线程开仓时等待
		actMgr.blockLock.acquire()
		#
		self.curParallelLevel = len(self.actionManagers)
		self.mgrLock.release()
		return True
	
	# 释放操作管理接口
	def freeManager (self,
		contract,	#合约
		):
		self.mgrLock.acquire()
		try:
			del self.actionManagers[contract]
			self.curParallelLevel = len(self.actionManagers)
		except KeyError:
			self.debug.error("freeManager: Found unknown %s" % contract)
		finally:
			self.mgrLock.release()

	# 返回并行执行状态
	def parallelStatus (self):
		return self.parallelLevel - self.curParallelLevel

	# 得到操作管理接口
	def getManager (self,
		contract,	#合约
		):
		return self.actionManagers[contract]

	# 唤醒阻塞的合约线程
	def __wakeupBlockedThread (self,
		actMgr,	#合约的操作管理接口
		action,	#
		):
		if action.type not in BLOCKED_ACTION_TYPES:
			return

		# 清除合约action队列的阻塞标志
		actMgr.actQueue.reqBlocked = False
		# 设置已通知标志为假，等待合约线程第一次握手
		actMgr.tagNotifyRecved = False
		# 唤醒被阻塞的合约线程
		actMgr.blockLock.release()
		# 已通知标志为真说明合约线程被唤醒，第一次握手结束
		while not actMgr.tagNotifyRecved:
			time.sleep(0.01)
		# 重新占锁以使能下一次开仓时阻塞
		actMgr.blockLock.acquire()
		# 再次设置已通知标志为假。第二次握手，主、合约线程都被唤醒且持锁正常
		actMgr.tagNotifyRecved = False
		self.debug.dbg("__wakeupBlockedThread: waked up %s." % action.contract)

	# 判定合约操作是否在工作队列中
	def __isContractInWorkQueue (self,
		contract,
		):
		_contracts = [ a.contract for a in self.workQueue ]
		# self.debug.dbg("__isContractInWorkQueue: %s _contracts %s" % (
		# 				contract, _contracts))
		return contract in _contracts

	# 初始化工作队列
	def __workQueueInit (self):
		"""
		从在工作队列中空缺（没有该合约的任何操作）的合约中选取action
		至工作队列中等待被执行、调度。
		"""
		actions = []
		for (contract, actMgr) in self.actionManagers.items():
			if self.__isContractInWorkQueue(contract):
				continue

			action = self.__workQueueSelect(contract)
			actions.append(action)

		self.__workQueueInsert(actions)
		# self.debug.dbg("workQueue %s" % self.workQueue)

		# 若前后两个action的tick发生变化则需要更新统计信息，
		# prevTick用于记录上一个action的tick。
		if self.prevTick is None:
			self.prevTick = self.workQueue[0].tick

	# 向工作队列插入action
	def __workQueueInsert (self,
		action,	#待插入操作
		):
		if isinstance(action, list):
			self.workQueue += action
		else:
			self.workQueue.append(action)

		# self.debug.dbg("type %s, workQueue %s" % (type(action), self.workQueue))
		# 最小的tick需最先被处理
		self.workQueue.sort(key = lambda x: x.tick)

	# 从工作队列取出action
	def __workQueuePop (self,
		index = 0,	#默认取出头一个
		):
		try:
			return self.workQueue.pop(index)
		except IndexError, e:
			self.debug.error("__workQueuePop: index %s, exp: %s" % (index, e))
			return None

	# 从合约的操作队列中选出action
	def __workQueueSelect (self,
		contract,	#合约
		):
		actMgr = self.getManager(contract)
		# 一直等待直到选取成功
		while True:
			action = actMgr.actQueue.popHead()
			# self.debug.dbg("__workQueueSelect: %s action %s" % (
			# 			contract, action.tick if action else action))
			if not action:
				time.sleep(0.1)
				continue
			return action

	# 处理合约操作
	def handleActions (self):
		self.__workQueueInit()

		while True:
			action = self.__workQueuePop(0)
			if not action:
				# 所有合约action已被执行完毕，退出
				return True

			curTick = action.tick
			oldPosNum = self.posMgr.curPos()
			actMgr = self.getManager(action.contract)
			self.debug.info("handleActions: %s tick %s, type %s, last tick %s" % (
					action.contract, action.tick, action.type,
					True if action.isLastTick else False))

			# 平仓
			if action.type == ACTION_CLOSE:
				# 释放仓位
				self.posMgr.free(action)
				# 统计平仓利润
				self.profitStat.add(DEF_CONTRACT, curTick, action.closeProfit)
				# 如果该次平仓结束后导致仓位变为０说明一次交易结束，需要结束该次利润统计
				if oldPosNum > 0 and self.posMgr.curPos() == 0:
					self.profitStat.end(action.contract, curTick)

			# 开仓
			elif action.type == ACTION_OPEN:
				# 设置分配标志
				actMgr.allowOpen = False
				# 分配仓位
				if self.posMgr.alloc(action):
					actMgr.allowOpen = True
					# 如果是第一个仓位则表示一次新交易开始，开始利润统计
					if oldPosNum == 0:
						self.profitStat.start(action.contract, curTick)

			# 尽早唤醒被阻塞的线程，提高执行效率
			self.__wakeupBlockedThread(actMgr, action)
			# 数据统计时可能用到
			actMgr.prevAction = action

			# tick发生变化则需要更新该tick内的统计信息，
			if curTick != self.prevTick:
				self.__countFloatingProfit(curTick)
			self.prevTick = curTick

			# 有合约结束，需分配新合约加入
			if action.isLastTick:
				self.freeManager(action.contract)
				return False

			newAction = self.__workQueueSelect(action.contract)
			self.__workQueueInsert(newAction)

	# 计算浮动利润
	def __countFloatingProfit (self,
		tick,
		):
		profit = 0
		# 轮询各合约的上一次操作，计算浮动利润
		for (contract, actMgr) in self.actionManagers.items():
			try:
				profit += actMgr.prevAction.floatProfit
			except AttributeError, e:
				profit += 0
		
		# 浮动利润巡航
		self.profitStat.navigate(DEF_CONTRACT, tick, profit)
	
	# 操作请求，合约发起请求接口
	def request (self,
		contract,	#合约
		tick,		#时间
		type,		#操作类型
		price,		#价格
		volume,		#开仓手数
		direction,	#方向
		floatProfit,	#浮动利润
		closeProfit = 0,	#平仓利润
		isLastTick = False,	#是否为最后一个tick
		):
		actMgr = self.getManager(contract)
		actMgr.actQueue.push(contract, tick, type, price, volume, 
					direction, floatProfit, closeProfit, isLastTick)
		
		if type == ACTION_SKIP:
			return True
		
		# 仓位操作需阻塞，等待主线程协调处理是否允许
		self.debug.dbg("%s: request: type %s, acquiring lock..." % (
						contract, type))
		# 阻塞，等待主线程分配
		actMgr.blockLock.acquire()
		# 主线程分配结束，并已设置分配状态。设置已通知标志，让主线程抢回锁
		actMgr.tagNotifyRecved = True
		actMgr.blockLock.release()
		# 让锁，检查等待确保主线程已抢回锁。主线程点锁后会设置已通知标志为假
		while actMgr.tagNotifyRecved:
			time.sleep(0.01)
		
		if type == ACTION_OPEN:
			# 返回主线程的协调结果
			return actMgr.allowOpen
		
		return True
	