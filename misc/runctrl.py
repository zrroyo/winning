#-*- coding:utf-8 -*-

'''
运行（执行）控制单元
'''

import time
from runstat import MarketRunStat
from priority import Priority

# Core run time conntrol block (RCB) between main thread and child thread.
class RunControl:
	def __init__ (self, acted, lock, tick, attrs, applied, startTick=None):
		self.acted = acted		# 'True' means child thread has taken action, 'False' 
						# means waitting for child thread to take action.
		self.lock = lock		# Lock to protect control attributes from changing.
		self.tick = tick		# Any time when tick varies, child thread needs checking
						# if should take actions.
		self.startTick = startTick	# The tick to start emulation thread.
		self.attrs = attrs		# Common attributes used for strategy to do regression.
		self.applied = applied		# 'True' means this control block is occupied by a thread.
		self.marRunStat = None		# The whole market run statistics block.
		return
	
	# Judge if self.tick matches a time tick.
	def tickMatch (self, timeTick):
		#print self.tick, timeTick
		t1 = time.strptime(self.tick, '%Y-%m-%d')
		t2 = time.strptime(timeTick, '%Y-%m-%d')
		
		return t1 == t2
		
	# Judge if self.tick is leg behind a time tick.
	def tickBehind (self, timeTick):
		#print self.tick, timeTick
		t1 = time.strptime(self.tick, '%Y-%m-%d')
		t2 = time.strptime(timeTick, '%Y-%m-%d')
		
		return t1 < t2
			
	# Do a micro HLT operation.
	def tinyHaltLoop (self):
		#time.sleep(0.01)
		return
	
	# Judge if a tick is ready for a strategy to take actions.
	def tickIsReady (self, 
		timeTick,	#策略工作tick（交易日）
		hookObj = None,	#需要辅助hook功能的对象，必须实现了tickBehindHook成员方法
		**extra		#hook操作所需参数
		):
		self.lock.acquire()
		#print timeTick, self.acted
		if self.acted:
			self.lock.release()
			self.tinyHaltLoop()
			return 'False'
		elif self.tickBehind(timeTick):
			''''
			注意：如果指定了hook对象，则需要为其调用hook操作来辅助其实现特定功能。
			'''
			if hookObj is not None:
				hookObj.tickBehindHook(self.tick, **extra)
				
			self.acted = True
			self.lock.release()
			self.tinyHaltLoop()
			return 'False'
		elif self.tickMatch(timeTick):
			self.lock.release()
			return 'True'
		else:
			#print "Thread TimeTick '%s' is lag behind tick '%s', synchronising..." % (timeTick, self.tick)
			self.lock.release()
			return 'SyncTick'
	
	# Set acted noticing main thread actions have been taken.
	def setActed (self):
		self.lock.acquire()
		self.acted = True
		self.lock.release()
		
		
# Run Time Control Block Set containing a set of Run Control blocks, 
# necessary for an emulation.
class RunCtrlSet:
	def __init__ (self, maxAllowedPos, tickSrc):
		self.num = 0
		self.set = []
		self.maxAllowedPos = maxAllowedPos
		self.tickSrc = tickSrc
		self.priMgr = Priority()
		return
	
	def __exit__ (self):
		return
	
	def nrRunCtrl (self):
		return len(self.set)
		
	# Append a Run Control block.	
	def add (self, attr):
		#if self.nrRunCtrl() < self.num:
		self.set.append(attr)
		self.priMgr.add(self.num)
		self.num += 1
		return self.nrRunCtrl()
	
	# Get the RCB indexed by @index.
	def getRunCtrl (self, index):
		return self.set[index]
	
	# Acquire the protection lock for RCB indexed by @index.
	def acquireLock (self, index):
		self.set[index].lock.acquire()
		
	# Release the protection lock for RCB indexed by @index.
	def releaseLock (self, index):
		self.set[index].lock.release()
		
	# Acquire protection locks for all RCBs.
	def acquireAllLocks (self):
		i = 0
		while (i < self.num):
			self.set[i].lock.acquire()
			i += 1
			
	# Release protection locks for all RCBs.
	def releaseAllLocks (self):
		i = 0
		while (i < self.num):
			self.set[i].lock.release()
			i += 1
		
	# Release protection locks in a descent priority order (bigger priority 
	# number, lower priority level) for all RCBs.
	def releaseAllLocksDescPriority (self):
		priList = self.priMgr.listPriorities()
		#print priList
		i = 0
		while (i < self.num):
			#print 'release lock %d' % priList[i][0]
			index = priList[i][0]
			self.set[index].lock.release()
			self.priMgr.priorityHaltLoop()
			i += 1
			
	# Return if a RCB is occupied.
	def isApplied (self, index):
		return self.set[index].applied
	
	# Set a RCB occupied.
	def setApplied (self, index):
		self.set[index].applied = True
		
	# Clear a RCB occupied.
	def clearApplied (self, index):
		self.set[index].applied = False
		
	# Return if all child threads are stopped.
	# Note, this will acquire all protection locks.
	def ifAllStoppedWithLocks (self):
		self.acquireAllLocks()
		allStopped = True
		i = 0
		while (i < self.num):
			if self.isApplied(i):
				allStopped = False
				break
			i += 1
		self.releaseAllLocks()
		return allStopped
				
	# Return if a child thread has taken actions after tick varied.
	def isActed (self, index):
		return self.set[index].acted
	
	# Set acted flag for RCB indexed by @index.
	def setActed (self, index):
		self.set[index].acted = True
			
	# Clear acted flag for RCB indexed by @index.
	def clearActed (self, index):
		self.set[index].acted = False
			
	# Set acted flag for all unapplied RCB. (applied == False).
	def setActedForUnapplied (self):
		i = 0
		while (i < self.num):
			if not self.set[i].applied:
				self.set[i].acted = True
			i += 1
			
	# Clear acted flag for all applied RCB. (applied == False).
	def clearActedForApplied (self):
		i = 0
		while (i < self.num):
			if self.set[i].applied:
				self.set[i].acted = False
			i += 1
			
	# Judge if all child threads have taken actions after tick varied.
	def ifAllActed (self):
		#self.acquireAllLocks()
		allActed = True
		i = 0
		while (i < self.num):
			if not self.isActed(i):
				allActed = False
				break
			i += 1
		#self.releaseAllLocks()
		return allActed
		
	# New a tick and set for all child threads.	
	def setNewTicks (self):
		newTick = self.tickSrc.tickNext()
		i = 0
		while (i < self.num):
			self.set[i].tick = newTick
			i += 1
		
	# Set a tick for all child threads.
	def setTick (self, timeTick):
		i = 0
		while (i < self.num):
			self.set[i].tick = timeTick
			i += 1
			
	# Enable doing statistics for a market.
	def enableMarketRunStat(self, mute=False):
		marRunStat = MarketRunStat(self.maxAllowedPos, mute)
		i = 0
		while (i < self.num):
			self.set[i].marRunStat = marRunStat
			i += 1
		