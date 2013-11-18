#-*- coding:utf-8 -*-

import sys
sys.path.append("..")

import strategy as STRT
from dataMgr.data import Data, CtpData
from date import Date

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
		
		self.workDay = None
		
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
	
	def openShortPostion (self, price):
		if self.curPostion() >= self.maxAddPos:
			return False
		
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			if not self.emuRunCtrl.marRunStat.openPosition():
				self.log("	@-.-@ Market max allowed positions are full!")
				return False
		
		self._pList.append(price)
		self.log("		-->> Open: %s, poses %s <<--" % (price, self.curPostion()))
		return True
		
	def openLongPostion (self, price):
		if self.curPostion() >= self.maxAddPos:
			return False
		
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			if not self.emuRunCtrl.marRunStat.openPosition():
				self.log("	@-.-@ Market max allowed positions are full!")
				return False
			
		self._pList.append(price)
		self.log("		-->> Open: %s, poses %s <<--" % (price, self.curPostion()))
		return True
		
	def closeShortPostion (self, price):
		if self.curPostion() == 0:
			return
		
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			if not self.emuRunCtrl.marRunStat.closePosition():
				return
			
		profit = self._pList.pop() - price
		profit *= self.minPos
		profit *= self.priceUnit
		self.profit += profit
		self.totalProfit += profit
		
		# If need do runtime statistics, update status.
		if self.runStat is not None:
			self.runStat.update(profit)
			
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			self.emuRunCtrl.marRunStat.update(profit)
			
		self.log("		<<-- Close: profit %s, poses %s -->>" % (profit, self.curPostion()+1))
		if self.curPostion() == 0:
			self.showProfit()
			# If need do runtime statistics, update status.
			if self.runStat is not None:
				self.runStat.updateBusinessProfit(self.profit)
			
			if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
				self.emuRunCtrl.marRunStat.updateBusinessProfit(self.profit)
				self.emuRunCtrl.marRunStat.showMarRunStat()
		
		return self.curPostion()
	
	def closeLongPostion (self, price):
		if self.curPostion() == 0:
			return
		
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			if not self.emuRunCtrl.marRunStat.closePosition():
				return
		
		profit = price - self._pList.pop()
		profit *= self.minPos
		profit *= self.priceUnit
		self.profit += profit
		self.totalProfit += profit
		
		# If need do runtime statistics, update status.
		if self.runStat is not None:
			self.runStat.update(profit)
			
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			self.emuRunCtrl.marRunStat.update(profit)
				
		self.log("		<<-- Close: profit %s, poses %s -->>" % (profit, self.curPostion()+1))
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
		while self.curPostion():
			if short is 'short':
				self.closeShortPostion(price)
			else:
				self.closeLongPostion(price)
					
		return self.curPostion()
			
	def closeMultPostion (self, poses, price, short):
		i = 0
		while self.curPostion() and i < poses:
			if short is 'short':
				self.closeShortPostion(price)
			else:
				self.closeLongPostion(price)
			i = i + 1
		
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
		self.mdAgent = mdAgent
		self.tdAgent = tdAgent
		self.data = CtpData(self.futName, self.database, self.dataTable, workDay, mdAgent)
			
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
		