#-*- coding:utf-8 -*-

import sys
sys.path.append("..")

import strategy as STRT
from dataMgr.data import Data, CtpData
from date import Date
from ctp.autopos import CtpAutoPosition

#
# Futures strategy super class which defines the most common methods 
# used to do futures business. Any futures strategy must inherit this 
# class so that the main framework could know how to interact with 
# a certain strategy.
#

class Futures(STRT.Strategy):
	def __init__ (self, 
		futName, 		#合约代号
		dataTable, 		#数据表名
		database='futures', 	#数据库名
		runStat=None		#运行时数据统计模块
		):
		self.futName = futName		# The future name to test.
		self.maxAddPos = None		# The max actions allowd to add for a business.
		self.minPos = None		# The minimum unit to add positions.
		self.minPosIntv = None		# The minimum interval to add positions.
		self.priceUnit = None		# Price unit.
		self._pList = []		# The list to contain all positions.
		self.totalProfit = 0		# Total profit in one time of test.
		self.profit = 0			# The current profit for a time of business.
		self.runStat = runStat		# Count runtime statistics.
		self.emuRunCtrl = None		# The emulation run control block.
		
		self.database = database
		self.dataTable = dataTable
		self.data = Data(database, dataTable)
		self.dateSet = Date(database, dataTable)
		
		self.workDay = None	#指定当前工作日
		self.ctpPos = None	#CTP服务器持仓管理接口
		
		return
	
	def __exit__ (self):
		return
	
	# The core method to run the whole test or business. Each strategy 
	# _MUST_ inherit this method and define your own one.
	def run (self):
		return
	
	# setAttrs() and checkAttrs() might be the key methods too, especially 
	# the tests which are sensitive to the values of maxAddPos, minPos, minPosIntv, 
	# etc. You need inherit and adjust these two method in your own occasions.
	def setAttrs (self, maxAddPos, minPos, minPosIntv, priceUnit):
		return
		
	def checkAttrs (self):
		return False
			
	def showProfit (self):
		self.log("		++++++ Business profit %s ++++++" % (self.profit))
		self.log("		****** Total profit %s ******" % (self.totalProfit))
	
	# Position Management Methods.
	def curPostion (self):
		return len(self._pList)
	
	def emptyPostion (self):
		self._pList = []
		self.profit = 0
	
	def openShortPosition (self, price):
		if self.curPostion() >= self.maxAddPos:
			return False
		
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			if not self.emuRunCtrl.marRunStat.openPosition():
				self.log("	@-.-@ Market max allowed positions are full!")
				return False
		
		#
		if self.ctpPos is not None and self.dateSet.extra == True:
			price = self.ctpPos.open_short_position(self.futName, price, self.minPos)
		
		self._pList.append(price)
		self.log("		-->> Open: %s, poses %s <<--" % (price, self.curPostion()))
		return price
		
	def openLongPosition (self, price):
		if self.curPostion() >= self.maxAddPos:
			return False
		
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			if not self.emuRunCtrl.marRunStat.openPosition():
				self.log("	@-.-@ Market max allowed positions are full!")
				return False
			
		#
		if self.ctpPos is not None and self.dateSet.extra == True:
			price = self.ctpPos.open_long_position(self.futName, price, self.minPos)
			
		self._pList.append(price)
		self.log("		-->> Open: %s, poses %s <<--" % (price, self.curPostion()))
		return price
		
	def closeShortPosition (self, price, poses):
		if self.curPostion() < poses:
			print 'close short position error'
			return
		
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			if not self.emuRunCtrl.marRunStat.closePosition(poses):
				return
			
		#
		if self.ctpPos is not None and self.dateSet.extra == True:
			price = self.ctpPos.close_short_position(self.futName, price, self.minPos * poses)
			
		profit = 0
		while poses > 0:
			vProfit = self._pList.pop() - price
			vProfit *= self.minPos
			vProfit *= self.priceUnit
			poses -= 1
			profit += vProfit
			self.log("		<<-- Close: profit %s, poses %s -->>" % (vProfit, self.curPostion()+1))
			
		self.profit += profit
		self.totalProfit += profit
		
		# If need do runtime statistics, update status.
		if self.runStat is not None:
			self.runStat.update(profit)
			
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			self.emuRunCtrl.marRunStat.update(profit)
			
		if self.curPostion() == 0:
			self.showProfit()
			# If need do runtime statistics, update status.
			if self.runStat is not None:
				self.runStat.updateBusinessProfit(self.profit)
			
			if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
				self.emuRunCtrl.marRunStat.updateBusinessProfit(self.profit)
				self.emuRunCtrl.marRunStat.showMarRunStat()
		
		return self.curPostion()
	
	def closeLongPosition (self, price, poses):
		if self.curPostion() < poses:
			print 'close long position error'
			return
		
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			if not self.emuRunCtrl.marRunStat.closePosition(poses):
				return
		
		#
		if self.ctpPos is not None and self.dateSet.extra == True:
			price = self.ctpPos.close_long_position(self.futName, price, self.minPos * poses)
			
		profit = 0
		while poses > 0:
			vProfit = self._pList.pop() - price
			vProfit *= self.minPos
			vProfit *= self.priceUnit
			poses -= 1
			profit += vProfit
			self.log("		<<-- Close: profit %s, poses %s -->>" % (vProfit, self.curPostion()+1))
				
		self.profit += profit
		self.totalProfit += profit
		
		# If need do runtime statistics, update status.
		if self.runStat is not None:
			self.runStat.update(profit)
			
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			self.emuRunCtrl.marRunStat.update(profit)
				
		if self.curPostion() == 0:
			self.showProfit()
			# If need do runtime statistics, update status.
			if self.runStat is not None:
				self.runStat.updateBusinessProfit(self.profit)
			
			if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
				self.emuRunCtrl.marRunStat.updateBusinessProfit(self.profit)
				self.emuRunCtrl.marRunStat.showMarRunStat()
				
		return self.curPostion()
		
	def closeAllPostion (self, price, short):
		poses = self.curPostion()
		if short is 'short':
			self.closeShortPosition(price, poses)
		else:
			self.closeShortPosition(price, poses)
			
		return self.curPostion()
			
	def closeMultPostion (self, poses, price, short):
		if short is 'short':
			self.closeShortPosition(price, poses)
		else:
			self.closeShortPosition(price, poses)
			
		return self.curPostion()
		
	# Export any assistant/helper information to users here.
	def assistant (self, extra):
		print '\nNo assistant found!\n'
		return
	
	# Switch on emulation mode. In emulation mode, strategy will be run in a 
	# thread and needs to update typically run() method (or other methods, such 
	# as, doShort, doLong, related to tick) to receive ticks from main thread 
	# (emulate.py module) and then take all operations proposed in one tick.
	def enableEmulate (self, runCtrl):
		self.emuRunCtrl = runCtrl
	
	#打开CTP模式
	def enableCTP (self, 
		workDay,	#交易日
		runCtrl, 	#CTP运行时控制模块
		mdAgent, 	#行情数据代理
		tdAgent		#交易服务器端代理
		):
		self.workDay = workDay
		self.ctpRunCtrl = runCtrl
		self.data = CtpData(self.futName, self.database, self.dataTable, workDay, mdAgent)
		self.ctpPos = CtpAutoPosition(mdAgent, tdAgent)
			
	# Manage storing logs.
	def log (self, logMsg, *args):
		logs = logMsg % (args)
		#logs = '%s>| %s' % (self.futName, logs)
		if self.emuRunCtrl:
			logs = '<%s> | %s' % (self.futName, logs)
			if self.emuRunCtrl.log:
				self.emuRunCtrl.log.append(logs)
			else:
				print logs	
		else:
			print logs
		