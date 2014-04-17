#-*- coding:utf-8 -*-

import sys
sys.path.append("..")

import strategy as STRT
from dataMgr.data import Data, CtpData
from date import Date
from ctp.autopos import CtpAutoPosition
from misc.posmgr import PositionMananger

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
		self.posMgr = None		#持仓管理接口
		self.totalProfit = 0		# Total profit in one time of test.
		self.profit = 0			# The current profit for a time of business.
		self.runStat = runStat		# Count runtime statistics.
		self.emuRunCtrl = None		# The emulation run control block.
		
		self.database = database
		self.dataTable = dataTable
		self.data = Data(database, dataTable)
		self.dateSet = Date(database, dataTable)
		
		self.workDay = None	#指定当前工作日
		self.startTime = None	#交易启动时间
		self.ctpPos = None	#CTP服务器持仓管理接口
		self.ctpPosOn = False	#CTP启动开关，True则可进行开平仓操作
		self.logMgr = None	#通用日志管理接口
		self.logPainter = None	#CTP日志管理接口
		self.logPainterLine = 1	#该合约在CTP日志管理所分配到的描绘行
		self.paintLogOn = False	#向终端窗口显示log
		
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
	def setAttrs (self, 
		maxAddPos,	#最大可加仓次数
		minPos,		#每次加仓最小手数
		minPosIntv,	#允许加仓的最小价格差
		priceUnit,	#每‘1’价格差对应的真实价格波动
		):
		self.maxAddPos = maxAddPos
		self.minPos = minPos
		self.minPosIntv = minPosIntv
		self.priceUnit = priceUnit
		self.posMgr = PositionMananger(maxAddPos)
		return
		
	def checkAttrs (self):
		return False
			
	def showProfit (self):
		self.log("		++++++ Business profit %s ++++++" % (self.profit))
		self.log("		****** Total profit %s ******" % (self.totalProfit))
	
	# Position Management Methods.
	def curPostion (self):
		return self.posMgr.numPositions()
	
	def emptyPostion (self):
		self.posMgr.emptyPosition()
		self.profit = 0
	
	#开空
	def openShortPosition (self, price):
		if self.curPostion() >= self.maxAddPos:
			return None
		
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			if not self.emuRunCtrl.marRunStat.openPosition():
				self.log("	@-.-@ Market max allowed positions are full!")
				return None
		
		#如果CTP启动开关被触发说明进入当前交易日，应进行实盘操作。
		if self.ctpPosOn == True:
			price = self.ctpPos.openShortPosition(self.futName, price, self.minPos)
		
		self.posMgr.pushPosition(price)
		self.log("		-->> Open: %s, poses %s <<--" % (price, self.curPostion()))
		return price
		
	#开多
	def openLongPosition (self, price):
		if self.curPostion() >= self.maxAddPos:
			return None
		
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			if not self.emuRunCtrl.marRunStat.openPosition():
				self.log("	@-.-@ Market max allowed positions are full!")
				return None
			
		#如果CTP启动开关被触发说明进入当前交易日，应进行实盘操作。
		if self.ctpPosOn == True:
			price = self.ctpPos.openLongPosition(self.futName, price, self.minPos)
			
		self.posMgr.pushPosition(price)
		self.log("		-->> Open: %s, poses %s <<--" % (price, self.curPostion()))
		return price
		
	#平空头仓位
	def closeShortPosition (self, 
		price,	#平仓价格
		poses	#仓数
		):
		if self.curPostion() < poses:
			print 'close short position error'
			return
		
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			if not self.emuRunCtrl.marRunStat.closePosition(poses):
				return
			
		#如果CTP启动开关被触发说明进入当前交易日，应进行实盘操作。
		if self.ctpPosOn == True:
			price = self.ctpPos.closeShortPosition(self.futName, price, self.minPos * poses)
			
		profit = 0
		while poses > 0:
			'''
			从仓位记录队列中移除，并统计每一单的赢利
			'''
			pos = self.posMgr.popPosition()
			orderProfit = pos.price - price
			orderProfit *= self.minPos
			orderProfit *= self.priceUnit
			poses -= 1
			profit += orderProfit
			
			# If need do runtime statistics, update status.
			if self.runStat is not None:
				self.runStat.update(orderProfit)
				
			if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
				self.emuRunCtrl.marRunStat.update(orderProfit)
			
			self.log("		<<-- Close: profit %s, poses %s -->>" % (orderProfit, self.curPostion()+1))
			
		self.profit += profit
		self.totalProfit += profit
			
		if self.curPostion() == 0:
			self.showProfit()
			# If need do runtime statistics, update status.
			if self.runStat is not None:
				self.runStat.updateBusinessMaxMinWin(self.profit)
			
			if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
				self.emuRunCtrl.marRunStat.updateBusinessMaxMinWin(self.profit)
				self.emuRunCtrl.marRunStat.showMarRunStat()
		
		return price
	
	#平多头仓位
	def closeLongPosition (self, 
		price,	#平仓价格
		poses	#仓数
		):
		if self.curPostion() < poses:
			print 'close long position error'
			return
		
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			if not self.emuRunCtrl.marRunStat.closePosition(poses):
				return
		
		#如果CTP启动开关被触发说明进入当前交易日，应进行实盘操作。
		if self.ctpPosOn == True:
			price = self.ctpPos.closeLongPosition(self.futName, price, self.minPos * poses)
			
		profit = 0
		while poses > 0:
			'''
			从仓位记录队列中移除，并统计每一单的赢利
			'''
			pos = self.posMgr.popPosition()
			orderProfit = price - pos.price
			orderProfit *= self.minPos
			orderProfit *= self.priceUnit
			poses -= 1
			profit += orderProfit
			
			# If need do runtime statistics, update status.
			if self.runStat is not None:
				self.runStat.update(orderProfit)
				
			if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
				self.emuRunCtrl.marRunStat.update(orderProfit)
			
			self.log("		<<-- Close: profit %s, poses %s -->>" % (orderProfit, self.curPostion()+1))
				
		self.profit += profit
		self.totalProfit += profit
				
		if self.curPostion() == 0:
			self.showProfit()
			# If need do runtime statistics, update status.
			if self.runStat is not None:
				self.runStat.updateBusinessMaxMinWin(self.profit)
			
			if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
				self.emuRunCtrl.marRunStat.updateBusinessMaxMinWin(self.profit)
				self.emuRunCtrl.marRunStat.showMarRunStat()
				
		return price
		
	#平掉所有仓位	
	def closeAllPostion (self, 
		price,	#平仓价格
		short	#多空标志
		):
		poses = self.curPostion()
		if short is 'short':
			return self.closeShortPosition(price, poses)
		else:
			return self.closeLongPosition(price, poses)
			
	#平掉多个仓位	
	def closeMultPostion (self, 
		poses,	#仓数
		price,	#平仓价格
		short	#多空标志
		):
		if short is 'short':
			return self.closeShortPosition(price, poses)
		else:
			return self.closeLongPosition(price, poses)
			
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
		startTime,	#交易启动时间
		runCtrl, 	#CTP运行时控制模块
		mdAgent, 	#行情数据代理
		tdAgent,	#交易服务器端代理
		logPainter=None,	#CTP日志管理接口
		logPainterLine = 1	#该合约在CTP日志管理所分配到的描绘行
		):
		'''
		在CTP实盘交易之前，需要确定到当前阶段的持仓情况。最简便的方法就是
		直接启动历史模拟来自动确定，从而确保最大化的遵循交易策略。
		注：目前暂不支持行情保存和重置。
		'''
		self.emuRunCtrl = runCtrl
		self.workDay = workDay
		self.startTime = startTime
		self.data = CtpData(self.futName, self.database, self.dataTable, workDay, mdAgent)
		self.ctpPos = CtpAutoPosition(mdAgent, tdAgent, self, 1)
		self.logPainter = logPainter
		self.logPainterLine = logPainterLine
		
	#开启日志记录.
	def enableStoreLogs(self, logMgr):
		self.logMgr = logMgr
		
	#日志（输出）统一接口
	def log (self, logMsg, *args):
		logs = logMsg % (args)
		if self.emuRunCtrl:
			logs = '<%s> | %s' % (self.futName, logs)
			
			#如果日志记录服务已启动，则需要写入日志文件。
			if self.logMgr is not None:
				self.logMgr.append(logs)
			else:
				print logs
				
			#如果CTP模式已启动并且需要显示动态跟踪行情，则将日志写至指定窗口中。
			if self.paintLogOn == True and self.logPainter is not None:
				logs = logMsg % (args)
				logs = '<%6s>| %s' % (self.futName, logs)
				self.logPainter.paintLine(self.logPainterLine, logs)
				
		else:
			print logs
		
	#数据统计，如，最高、低利润，回撤率等
	def doStatistics (self, 
		time,		#交易日
		price,		#价格
		direction,	#多空方向
		action,		#是统计RunStat还是MarketRunStat
		):
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat or self.runStat is not None:
			profit = 0.0
			numPoses = self.posMgr.numPositions()
			while numPoses > 0:
				pos = self.posMgr.getPositionByNum(numPoses)
				if direction == 'long':
					interval = price - pos.price
				else:
					interval = pos.price - price
					
				interval *= self.minPos
				interval *= self.priceUnit
				profit += interval
				numPoses -= 1
				
			if action == 'MarketRunStat':
				self.emuRunCtrl.marRunStat.updateMaxMinProfit(profit, time)
			elif action == 'RunStat':
				self.runStat.updateMaxMinProfit(profit, time)
		