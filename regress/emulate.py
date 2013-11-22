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
from misc.runstat import RunStat
from misc.runctrl import RunControl, RunCtrlSet
from misc.logmgr import Log


# Common attributes used for strategy to do regression. 
class CommonAttrs:
	def __init__ (self, maxAddPos, minPos, minPosIntv, priceUnit):
		self.maxAddPos = maxAddPos
		self.minPos = minPos
		self.minPosIntv = minPosIntv
		self.priceUnit = priceUnit
		return
		
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
	runStat = RunStat(futCode)
	
	if strategy == 'turt1':
		#strt1 = turt1.Turt1 (futCode, '%s_dayk' % futCode, 'dummy', 'history', runStat)
		strt1 = turt1.Turt1 (futCode, futCode, 'dummy', 'history', runStat)
	else:
		print "Bad strategy, only supports 'turt1' right now..."
		emulationThreadEnd(runCtrl)
		return
		
	# Enable storing logs.
	logTemp = 'logs/%s.log' % futCode	
	futLog = Log(logTemp)
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
	
	