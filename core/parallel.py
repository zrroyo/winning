#-*- coding:utf-8 -*-

'''
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2015年 07月 05日 星期日 18:02:02 CST

并行执行模块
'''

import sys
sys.path.append("..")
import thread
from time import *
from datetime import timedelta

from misc.debug import *
from misc.dateTime import *
from signal import *
from statistics import *

#操作类型
ACTION_OPEN	= "OPEN"
ACTION_CLOSE	= "CLOSE"
ACTION_SKIP	= "SKIP"

#ParaCore（巡航时）默认合约名
DEF_CONTRACT	= "paraCore"

#操作记录
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

#操作记录队列
class ActionQueue:
	
	actQueue = []	#操作记录队列
	
	def __init__ (self,
		tickFormat,	#Tick格式
		debug = False,	#是否调试
		):
		self.debug = Debug('ActionQueue', debug)	#调试接口
		self.tickFormat = tickFormat
		#保护锁
		self.lock = thread.allocate_lock()
		#同步窗口
		self.syncWindow = None
		#同步窗口内的操作已就绪
		self.readyToSelect = False
		#遇到需阻塞的操作请求
		self.reqBlocked = False
		#已遇到最后一个操作记录，预示合约结束
		self.onLastTick = False
	
	#将请求压入操作队列
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
		self.debug.info("tick %s, type %s, price %s, syncWindow %s" % (
				strToDatetime(tick, self.tickFormat), type, price, self.syncWindow))
		#操作时间大于同步窗口则说明同步窗口内的所有操作已就绪
		if not self.readyToSelect and strToDatetime(tick, self.tickFormat) >= self.syncWindow:
			self.readyToSelect = True
		
		#如果是开、平仓则需要阻塞，设置请求阻塞标志
		if type != ACTION_SKIP:
			self.reqBlocked = True
		
		#如果是最后一个操作需提示paraCore结束合约
		if isLastTick:
			self.onLastTick = True
		
		self.lock.release()
		self.debug.dbg("push: readyToSelect %s, reqBlocked %s, onLastTick %s" % (
					self.readyToSelect, self.reqBlocked, self.onLastTick))
	
	#设置下一个同步窗口
	def setSyncWindow (self,
		syncWindow,	#同步窗时间戳
		):
		self.lock.acquire()
		self.syncWindow = syncWindow
		self.readyToSelect = False
		self.lock.release()
	
	#得到操作队列的头元素
	def getHead (self):
		try:
			return self.actQueue[0]
		except:
			return None
	
	#删除操作队列的头元素
	def deleteHead (self):
		try:
			del(self.actQueue[0])
		except:
			pass

#操作管理。每个合约都需要分配一个单独操作管理接口。
class ActionManager:
	def __init__ (self):
		self.actQueue = None	#操作记录队列接口
		self.prevAction = None	#上一个操作记录
		
		#阻塞锁，有阻塞请求时阻塞合约线程。
		self.blockLock = thread.allocate_lock()
		#允许开仓
		self.allowOpen = False
		#通知已接受标志
		self.tagNotifyRecved = False

#合约操作类，绑定合约和操作。
class ContractAction:
	def __init__ (self,
		contract,	#
		action,		#
		):
		self.contract = contract
		self.action = action

#仓位管理
class PositionAllocator:
	def __init__ (self,
		maxVolume,	#最大允许仓位
		debug = False,	#是否调试
		):
		self.debug = Debug('PositionAllocator', debug)	#调试接口
		self.maxVolume = maxVolume
		self.available = maxVolume	#剩余仓位
	
	#分配仓位
	def alloc (self,
		action,	#操作记录
		):
		#如果申请数大于剩余数则失败
		if action.volume > self.available:
			self.debug.dbg("Alloc not allowed, maxVolume %s, available %s, required %s" % (
							self.maxVolume, self.available, action.volume))
			return False
		
		self.available -= action.volume
		return True
	
	#释放仓位
	def free (self,
		action,	#操作记录
		):
		self.available += action.volume
		return True
	
	#返回当前的仓位
	def curPos (self):
		return self.maxVolume - self.available
		

#并行测试／执行控制核心
class ParallelCore:
	
	actionManagers = {}	#操作管理队列
	actionsPoll = []	#操作记录池
	tickRefs = {}		#交易时间引用记录
	
	def __init__ (self,
		startTick,	#开始tick
		interval,	#同步窗口间隔
		maxVolume,	#最大允许的仓位数
		dumpName,	#统计信息Dump名
		debug = False,	#是否调试
		):
		self.debug = Debug('ParallelCore', debug)	#调试接口
		self.dbgMode = debug
		self.interval = interval
		self.tickFormat = self.__detectTickFormat(startTick)	#tick格式
		#Fix me!
		self.nextSyncWindow = strToDatetime(startTick, self.tickFormat)
		self.debug.dbg("__init__: nextSyncWindow %s" % self.nextSyncWindow)
		#仓位管理接口
		self.posMgr = PositionAllocator(maxVolume, debug)
		#利润统计接口
		self.profitStat = ProfitStat(dumpName, debug)
		#退出并行模拟标志
		self.tagStopHandling = False
	
	#检测tick格式
	def __detectTickFormat (self,
		tick,
		):
		time = tick.split(' ')
		if len(time) == 2:
			format = "%Y:%m:%d %H:%M:%S"
		else:
			format = "%Y:%m:%d"
		
		if tick.find('-') != -1:
			sep = '-'
		
		format = format.replace(':', sep,)
		self.debug.dbg("__detectTickFormat: Tick format: %s" % format)
		return format
	
	#分配操作管理接口
	def allocManager (self,
		contract,	#合约
		):
		actMgr = ActionManager()
		actMgr.actQueue = ActionQueue(self.tickFormat, self.dbgMode)
		self.actionManagers[contract] = actMgr
		#占住阻塞锁以保证合约线程开仓时等待
		actMgr.blockLock.acquire()
		return actMgr
	
	#释放操作管理接口
	def freeManager (self,
		contract,	#合约
		):
		pass
	
	#得到操作管理接口
	def getManager (self,
		contract,	#合约
		):
		return self.actionManagers[contract]
	
	#Tick索引加一
	def __tickRefsInc (self,
		tick,
		):
		try:
			self.tickRefs[tick] += 1
		except:
			self.tickRefs[tick] = 1
	
	#Tick索引减一
	def __tickRefsDec (self,
		tick,
		):
		try:
			self.tickRefs[tick] -= 1
		except:
			pass
	
	#得到Tick索引
	def __tickRefsGet (self,
		tick,
		):
		return self.tickRefs[tick]
	
	#删除所有Tick索引
	def __tickRefsDestroy (self):
		self.tickRefs.clear()
	
	#选择已就绪的操作集
	def __select (self,
		actionQueue,	#操作队列
		):
		#确保action全部就绪，或是有阻塞的action发生
		while True:
			actionQueue.lock.acquire()
			if actionQueue.readyToSelect or actionQueue.reqBlocked or actionQueue.onLastTick:
				break
			
			#如没有就绪则继续等待
			actionQueue.lock.release()
			sleep(0.1)
		
		'''
		syncWindow内的action已就绪，或是一个阻塞的action发生
		'''
		ret = []
		while True:
			action = actionQueue.getHead()
			if action == None:
				break
			
			#窗口内的所有action就绪
			if strToDatetime(action.tick, self.tickFormat) > self.nextSyncWindow:
				break
			
			ret.append(action)
			actionQueue.deleteHead()
			#tick索引加一
			self.__tickRefsInc(action.tick)
			#如果开仓，说明contract线程阻塞，不会有新action到来，选择结束
			#或是已经是最后一个action，不会再有新action到来，结束
			if action.type != ACTION_SKIP or action.isLastTick:
				break
		
		#选择结束需释放锁
		actionQueue.lock.release()
		return ret
	
	#将已选操作加入操作池
	def __actionsPollInsert (self,
		contract,	#合约
		actList,	#已选操作
		):
		for action in actList:
			newAction = ContractAction(contract, action)
			element = {"todo": newAction, "tick": action.tick}
			self.actionsPoll.append(element)
	
	#从操作池中删除操作
	def __actionsPollRemove (self,
		index,	#索引号
		):
		try:
			del self.actionsPoll[index]
		except:
			pass
	
	#对操作池排序
	def __actionsPollSorted (self):
		self.actionsPoll = sorted(self.actionsPoll, key = lambda x:x['tick'])
	
	#刷新操作池中的操作
	def __freshActionsTodo (self):
		#轮询各合约的操作队列，选取已就绪操作
		for (contract, actMgr) in self.actionManagers.items():
			actList = self.__select(actMgr.actQueue)
			self.__actionsPollInsert(contract, actList)
			
		#对操作池排序
		self.__actionsPollSorted()
		self.debug.dbg("__freshActionsTodo: actionsPoll: %s" % self.actionsPoll)
	
	#唤醒阻塞的合约线程
	def __wakeupBlockedThread (self,
		actMgr,	#合约的操作管理接口
		):
		#清除合约action队列的阻塞标志
		actMgr.actQueue.reqBlocked = False
		#设置已通知标志为假，等待合约线程第一次握手
		actMgr.tagNotifyRecved = False
		#唤醒被阻塞的合约线程
		actMgr.blockLock.release()
		#已通知标志为真说明合约线程被唤醒，第一次握手结束
		while not actMgr.tagNotifyRecved:
			sleep(0.01)
		#重新占锁以使能下一次开仓时阻塞
		actMgr.blockLock.acquire()
		#再次设置已通知标志为假。第二次握手，主、合约线程都被唤醒且持锁正常
		actMgr.tagNotifyRecved = False
		self.debug.dbg("__wakeupBlockedThread: Main tread acquired the blocklock.")
	
	#处理操作池中的操作。并行模拟核心。
	def __handleActions (self):
		#轮流处理操作池中所有就绪的操作。
		numActions = len(self.actionsPoll)
		for i in range(numActions):
			element = self.actionsPoll[0]
			todo = element["todo"]
			action = todo.action
			curTick = action.tick
			actMgr = self.getManager(todo.contract)
			oldPosNum = self.posMgr.curPos()
			self.debug.dbg("__handleActions: tick %s, type %s" % (action.tick, action.type))
			
			#平仓
			if action.type == ACTION_CLOSE:
				#释放仓位
				self.posMgr.free(action)
				#统计平仓利润
				self.profitStat.add(DEF_CONTRACT, curTick, action.closeProfit)
				#如果该次平仓结束后导致仓位变为０说明一次交易结束，需要结束该次利润统计
				if oldPosNum > 0 and self.posMgr.curPos() == 0:
					self.profitStat.end(action.contract, curTick)
				
				#启动被阻塞的线程
				self.__wakeupBlockedThread(actMgr)
			
			#开仓
			elif action.type == ACTION_OPEN:
				#设置分配标志
				actMgr.allowOpen = False
				#分配仓位
				if self.posMgr.alloc(action):
					actMgr.allowOpen = True
					#如果是第一个仓位则表示一次新交易开始，开始利润统计
					if oldPosNum == 0:
						self.profitStat.start(action.contract, curTick)
				
				#启动被阻塞的线程
				self.__wakeupBlockedThread(actMgr)
			
			#记录该次操作以备数据统计时用到
			actMgr.prevAction = action
			
			#Tick索引减一，如果为０则说明没有其它合约触发同一tick，可以统计tick数据
			self.__tickRefsDec(curTick)
			if self.__tickRefsGet(curTick) == 0:
				self.__countFloatingProfit(curTick)
			
			#action处理完毕，从action poll中移除
			self.__actionsPollRemove(0)
			
			#已经到最后一个action，设置结束标志，退出主循环
			if action.isLastTick:
				self.tagStopHandling = True
			
			#把唤醒开仓阻塞线程和重新选择action分开，以使得利润统计等能够与被阻塞线程并行
			if action.type != ACTION_SKIP:
				#
				self.debug.dbg("select actions for %s ..." % action.contract)
				newActions = self.__select(actMgr.actQueue)
				self.__actionsPollInsert(action.contract, newActions)
				break
	
	#为所有合约设置同步窗口
	def setSyncWindowForContracts (self):
		#同步窗口内的action全部处理完毕，设置下一个同步窗口
		self.nextSyncWindow += timedelta(days = self.interval)	#Fix Me! minutes = self.interval
		self.debug.error("setSyncWindowForContracts: nextSyncWindow %s" % self.nextSyncWindow)
		
		for (contract, actMgr) in self.actionManagers.items():
			actMgr.actQueue.setSyncWindow(self.nextSyncWindow)
	
	#处理合约操作
	def handleActions (self):
		while not self.tagStopHandling:
			#刷新操作池
			self.__freshActionsTodo()
			#如果操作池不为空则需要继续处理
			while len(self.actionsPoll) > 0:
				self.__handleActions()
				self.debug.dbg("handleActions: actionsPoll: %s" % self.actionsPoll)
			
			#操作池为空则说明该窗口内的所有tick已处理，清空tick索引进入下一窗口
			self.__tickRefsDestroy()
			#为所有合约设置下一同步窗口
			self.setSyncWindowForContracts()
	
	#计算浮动利润
	def __countFloatingProfit (self,
		tick,
		):
		profit = 0
		#轮询各合约的上一次操作，计算浮动利润
		for (contract, actMgr) in self.actionManagers.items():
			try:
				profit += actMgr.prevAction.floatProfit
			except:
				profit += 0
		
		#浮动利润巡航
		self.profitStat.navigate(DEF_CONTRACT, tick, profit)
	
	#操作请求。合约发起请求接口。
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
		
		#仓位操作需阻塞，等待主线程协调处理是否允许
		self.debug.dbg("request: type %s, acquiring lock..." % type)
		#阻塞，等待主线程分配
		actMgr.blockLock.acquire()
		#主线程分配结束，并已设置分配状态。设置已通知标志，让主线程抢回锁
		actMgr.tagNotifyRecved = True
		actMgr.blockLock.release()
		#让锁，检查等待确保主线程已抢回锁。主线程点锁后会设置已通知标志为假
		while actMgr.tagNotifyRecved:
			sleep(0.01)
		
		if type == ACTION_OPEN:
			#返回主线程的协调结果
			return actMgr.allowOpen
		
		return True
	