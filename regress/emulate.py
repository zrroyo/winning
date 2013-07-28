#! /usr/bin/python

'''
Emulation subsystem is capable of running a set of regression tests 
parallelly which could be better simulate real Future trading.

Ruan Zhengwang (ruan.zhengwang@gmail.com)
'''

import sys
sys.path.append('..')
import thread
import time
import strategy.turt1 as turt1
import tick
import runstat
import misc.priority as priority
import misc.logmgr as logmgr


# Common attributes used for strategy to do regression. 
class CommonAttrs:
	def __init__ (self, maxAddPos, minPos, minPosIntv, priceUnit):
		self.maxAddPos = maxAddPos
		self.minPos = minPos
		self.minPosIntv = minPosIntv
		self.priceUnit = priceUnit
		return

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
		self.log = None			# Log object if not None, which helps manage logs in regression.
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
	def tickIsReady (self, timeTick):
		self.lock.acquire()
		#print timeTick, self.acted
		if self.acted:
			self.lock.release()
			self.tinyHaltLoop()
			return 'False'
		elif self.tickBehind(timeTick):
			self.acted = True
			self.lock.release()
			self.tinyHaltLoop()
			return 'False'
		elif self.tickMatch(timeTick):
			self.lock.release()
			return 'True'
		else:
			print "Thread TimeTick '%s' is lag behind tick '%s', synchronising..." % (timeTick, self.tick)
			self.lock.release()
			return 'SyncTick'
	
	# Set acted noticing main thread actions have been taken.
	def setActed (self):
		self.lock.acquire()
		self.acted = True
		self.lock.release()
		
	# Enable storing logs.
	def enableStoreLogs(self, logObj):
		self.log = logObj
		
		
# Run Time Control Block Set containing a set of Run Control blocks, 
# necessary for an emulation.
class RunCtrlSet:
	def __init__ (self, maxAllowedPos, tickSrc):
		self.num = 0
		self.set = []
		self.maxAllowedPos = maxAllowedPos
		self.tickSrc = tickSrc
		self.marRunStat = runstat.MarketRunStat(maxAllowedPos)
		self.priMgr = priority.Priority()
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
	def enableMarketRunStat(self):
		i = 0
		while (i < self.num):
			self.set[i].marRunStat = self.marRunStat
			i += 1
			
# End call for an emulation thread.
def emulationThreadEnd (runCtrl):
	runCtrl.lock.acquire()
	runCtrl.applied = False
	
	# Do not set acted flag because it's possible to leave chance for main 
	# thread to upate tick to next. Instead, we only let new thread using 
	# this block to update acted flag itself or main thread set it while 
	# this block is in unapplied status.
	
	#runCtrl.acted = True
	runCtrl.lock.release()
	
	if runCtrl.log:
		runCtrl.log.close()
		
	thread.exit_thread()
	return

# Entry for an emulation thread.
def emulationThreadStart (strategy, futCode, runCtrl):
	strt1 = None
	runStat = runstat.RunStat(futCode)
	
	if strategy == 'turt1':
		#strt1 = turt1.Turt1 (futCode, '%s_dayk' % futCode, 'dummy', 'history', runStat)
		strt1 = turt1.Turt1 (futCode, futCode, 'dummy', 'history', runStat)
	else:
		print "Bad strategy, only supports 'turt1' right now..."
		emulationThreadEnd(runCtrl)
		return
		
	# Enable storing logs.
	logTemp = 'logs/%s.log' % futCode	
	futLog = logmgr.Log(logTemp)
	#runCtrl.enableStoreLogs(futLog)
	
	strt1.setAttrs(runCtrl.attrs.maxAddPos, runCtrl.attrs.minPos, 
			runCtrl.attrs.minPosIntv, runCtrl.attrs.priceUnit)
			
	# Enable emulation mode for strategy.	
	strt1.enableEmulate(runCtrl)
	strt1.run()
	if strt1.runStat is not None:
		strt1.runStat.showStat()
		
	emulationThreadEnd(runCtrl)

# Emulation Core.
class Emulate:
	def __init__ (self, strategy, ctrlSet, futList):
		self.strategy = strategy
		self.ctrlSet = ctrlSet
		self.futList = futList
		return
	
	def __exit__ (self):
		return
			
	# Core method to run a emulation.
	def run (self):
		# At the first beginning, no thread is running, so directly set current tick with no lockings.
		self.ctrlSet.setTick(self.ctrlSet.tickSrc.curTick())
		
		# Exits loop only when Futures list is empty and all child threads are stopped.
		while len(self.futList) != 0 or not self.ctrlSet.ifAllStoppedWithLocks():
			# if Futures list is not empty, allocate a RCB for the 
			# top Future and emulate it in a thread.
			if len(self.futList) != 0:
				i = 0
				while i < self.ctrlSet.num:
					self.ctrlSet.acquireLock(i)
					if not self.ctrlSet.isApplied(i):
						# If startTick is not None, we need wait until the tick 
						# matching start tick arrives.
						if self.ctrlSet.getRunCtrl(i).startTick is not None:
							if self.ctrlSet.tickSrc.curTickBehind(self.ctrlSet.getRunCtrl(i).startTick ):
								# If start tick didn't arrive, need to set acted flag,
								# otherwise will block tick source generate new tick.
								self.ctrlSet.setActed(i)
								self.ctrlSet.releaseLock(i)
								i += 1
								continue
							else:
								# Start tick arrived, clear acted flag and leave it to 
								# be set by emulation thread itself. And clear start
								# tick, we don't use it any more.
								self.ctrlSet.clearActed(i)
								self.ctrlSet.getRunCtrl(i).startTick = None
						
						if len(self.futList) == 0:
							self.ctrlSet.releaseLock(i)
							break
						
						futCode = self.futList.pop()
						self.ctrlSet.setApplied(i)
						print '# %s priority %d, priMgr list %s' % (futCode, self.ctrlSet.priMgr.updatePriority(i), self.ctrlSet.priMgr.listPriorities())
						self.ctrlSet.releaseLock(i)
						
						print 'Thread %d:' % i
						thread.start_new_thread(emulationThreadStart, 
								(self.strategy, futCode, self.ctrlSet.getRunCtrl(i)))
					else:
						self.ctrlSet.releaseLock(i)
					i += 1
			else:
				# When futures list is empty, all unapplied RCBs will never be allocated and
				# used again. And because if one of the acted flags is not set, new tick will
				# not be generated and then block child threads to run, so we need to set acted
				# flag for all unapplied RCBs at this point.
				self.ctrlSet.setActedForUnapplied()
				
			
			# Check if all child threads have taken actions after tick varied previously.
			# If all acted, set next tick and notice child threads to continue.
			
			#time.sleep(0.01)
			self.ctrlSet.acquireAllLocks()
			allActed = self.ctrlSet.ifAllActed()
			#print 'allActed %s' % (allActed)
			if allActed:
				self.ctrlSet.setNewTicks()
				self.ctrlSet.clearActedForApplied()
			
			self.ctrlSet.releaseAllLocksDescPriority()
		
if __name__ == '__main__':
	#futList = ['m0401', 'm0501', 'm0601', 'm0701', 'm0801']
	futList = ['m0401', 'm0409', 'm0501', 'm0509']
	#futList = ['m0401', 'm0409', 'm0501']
	#futList = ['m0401']
	futList.reverse()
	comAttr = CommonAttrs(4, 1, 40, 10)
	runCtrl1 = RunControl(False, thread.allocate_lock(), None, comAttr, False)
	#runCtrl2 = RunControl(False, thread.allocate_lock(), None, comAttr, False)
	runCtrl2 = RunControl(False, thread.allocate_lock(), None, comAttr, False, '2003-10-15')
	
	#tickSrc = tick.Tick(2003, 1, 1)
	tickSrc = tick.Tick(2003, 5, 18)
	
	runCtrlSet = RunCtrlSet(6, tickSrc)
	runCtrlSet.add(runCtrl1)
	runCtrlSet.add(runCtrl2)
	
	runCtrlSet.enableMarketRunStat()
	
	emu = Emulate('turt1', runCtrlSet, futList)
	emu.run()
	
	