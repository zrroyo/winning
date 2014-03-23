#-*- coding:utf-8 -*-

import sys
sys.path.append("..")
from time import sleep, strptime
import trade
import date as DATE
import db.mysqldb as sql
import futures as FUT


class TurtData:
	def __init__ (self, database, table):
		self.db = sql.MYSQL("localhost", 'win', 'winfwinf', database)
		self.table = table
		self.db.connect()
		return
		
	def __exit__ (self):
		self.db.close()
		return
		
	def updateTr (self, time, ltr):
		cond = 'Time=\'%s\'' % (time)
		value = 'Tr=%s' % (ltr)
		#print cond, value
		self.db.update(self.table, cond, value)
		return
	
	def updateAtr (self, time, atr):
		cond = 'Time=\'%s\'' %(time)
		value = 'Atr=%s' % (atr)
		#print cond, value
		self.db.update(self.table, cond, value)
		return
		
	# Check whether 'Atr' field in data table are all calculated.
	def checkAtr (self):
		cond = 'Atr is NULL'
		
		res = self.db.search (self.table, cond)
		if res > 0:
			return False
		else:
			return True
		
	# Get the 'Atr' filed for a record specified by @time
	def getAtr (self, time):
		cond = 'Time=\'%s\'' % (time)
		
		self.db.search (self.table, cond, 'Atr')
		res = self.db.fetch(0)
		#print res

		return res[0]
		
class Turtle(FUT.Futures):
	def __init__ (self, futName, dataTable, tradeTable, database='futures', runStat=None):
		FUT.Futures.__init__(self, futName, dataTable, database, runStat)
		self.tradeTable = tradeTable
		#self.tradeRec = trade.Trade(database, tradeTable)
		self.workMode = None
		self.turtData = None
		
		#print "Turtle initialized!"
		return
	
	def __exit__ (self):
		FUT.Futures.__exit__(self)
		return
	
	# Below are helper functions used to update Tr and Atr, and only used locally.
	def __updateTr (self, table, time, ltr):
		#print time, 'ltr', ltr
		turtDat = TurtData(self.database, table)
		return turtDat.updateTr(time, ltr)
		
	def __updateAtr (self, table, time, atr):
		#print time, '                          atr', atr
		turtDat = TurtData(self.database, table)
		return turtDat.updateAtr(time, atr)
	
	def __updateAtrFromTo (self, table, tFrom, tTo, atr):
		lcDateSet = DATE.Date(self.database, table)
		time = tFrom	
		lcDateSet.setCurDate(tFrom)
		
		while time is not None and time != tTo:
			self.__updateAtr(table, time, atr)
			time = lcDateSet.getSetNextDate()
			
		self.__updateAtr(table, tTo, atr)
	
	#def updateAtrFromTo (self, table, tFrom, tTo, atr):
		#return self.__updateAtrFromTo (table, tFrom, tTo, atr)
	
	def tr (self, time):
		t = '%s' % (time)
		if self.dateSet.isFirstDate(t):
			#print self.data.getHighest(t), self.data.getLowest(t)
			ltr = self.data.getHighest(t) - self.data.getLowest(t)
		else:
			prevClose = self.data.getClose(self.dateSet.prevDate(t))
			highest = self.data.getHighest(t)
			lowest = self.data.getLowest(t)
			
			#print prevClose, highest, lowest
			#print highest-lowest, highest - prevClose, prevClose - lowest
			ltr = max(highest-lowest, highest - prevClose, prevClose - lowest)

		return ltr
		
	def atr (self):
		table = self.dataTable
	
		i = 0
		atr = 0
		prevAtr = 0
		lcDateSet = DATE.Date(self.database, table)
		time = lcDateSet.firstDate()
		firstDate = time
		
		while time is not None:
			ltr = self.tr(time)
			#print 'ltr', ltr, 'prevAtr', prevAtr
			self.__updateTr(table, time, ltr)
			
			# For the beginning 20 dates, atr = (tr1 + tr2 + ... + tr20)/20
			if i < 20:
				atr = atr + ltr
				if i == 19:
					atr = atr/20
					self.__updateAtrFromTo(table, firstDate, time, atr)
					prevAtr = atr
				i = i + 1
				time= lcDateSet.getSetNextDate()
				continue
				
			# From the 21st time, atr = (prevAtr * 19 + ltr)/20
			atr = round((prevAtr * 19 + ltr)/20)
			self.__updateAtr(table, time, atr)
			#print 'atr', atr
			prevAtr = atr
			time= lcDateSet.getSetNextDate()
	
		return
	
	def query (self):
		return
			
	def checkAttrs (self):
		if self.maxAddPos is None:
			return False
		elif self.minPos is None:
			return False
		elif self.priceUnit is None:
			return False
		
		# If minPosIntv is not set, use ATR as minPosIntv by default.
		if self.minPosIntv is None:
			self.workMode = 'atr'
			self.turtData = TurtData(self.database, self.dataTable)
			if self.turtData.checkAtr() == False:
				print "	Turtle: Calculating ATRs for '%s'" % self.dataTable
				self.atr()
		
		return True
	
	def doShort (self, dateSet, date):
		return
		
	def doLong (self, dateSet, date):
		return
	
	def hitShortSignal (self, date, price):
		return
		
	def hitLongSignal (self, date, price):
		return
	
	# End of a test run. Close all opened positions before stop test.
	def endRun (self, mode):
		if self.curPostion():
			time = self.dateSet.lastDate()
			price = self.data.getClose(time)
			price = self.closeAllPostion(price, mode)
			self.log("	[%s] [%s] Clear all! close %s" % (mode, time, price))
			
		return
		
	def run (self):
		if self.checkAttrs() is False:
			print """
			Key attributss must be set before run strategy, which could be 
			simply made calling setAttrs().
			"""
			return
		
		if self.emuRunCtrl is not None:
			self.log('\n\n	<<<<<<<<<<< Run %s (Emulated Mode) >>>>>>>>>>>	\n\n' % self.futName)
		else:
			self.log('\n\n	<<<<<<<<<<< Run %s >>>>>>>>>>>	\n\n' % self.futName)
		
		lcDateSet = DATE.Date(self.database, self.dataTable)
		#lcDateSet = self.dateSet
		time = lcDateSet.firstDate()
		
		try:
			days = 0
			mode = None
			
			while time is not None:
				if self.emuRunCtrl is not None:
					tickReady = self.emuRunCtrl.tickIsReady(time)
					#print tickReady
					if tickReady == 'False':
						continue
					elif tickReady == 'SyncTick':
						time = lcDateSet.getSetNextDate()
						continue
				else:
					days += 1
					if days <= 10:
						time = self.moveToNextTick(lcDateSet)
						continue
				
				price = self.data.getClose(time)
				
				if self.hitShortSignal(time, price):
					mode = 'short'
					time = self.doShort(lcDateSet, time);
					# It also possibly hits the Long signal after quit short 
					# mode in same day.
					continue
				elif self.hitLongSignal(time, price):
					mode = 'long'
					time = self.doLong(lcDateSet, time);
					# It also possibly hits the Short signal after quit long 
					# mode in same day.
					continue
				else:
					mode = None
	
				time = self.moveToNextTick(lcDateSet, 
							price = self.data.getClose(time), 
							direction = mode
							)
				
			if mode is not None:
				self.endRun(mode)
		except:
			self.log('Exception on trading! Please check connection if working in CTP.')
			#self.log('交易执行异常，请检查远端服务器链接')
			return
	
	# Get the lowest value for a field within recent $days excluding $date.
	def lowestBeforeDate (self, date, days, field='Close'):
		return self.data.lowestBeforeDate(date, days, field)
		
	# Get the highest value for a field within recent $days excluding $date.
	def highestBeforeDate (self, date, days, field='Close'):
		return self.data.highestBeforeDate(date, days, field)
	
	# Return the lowest value in $days up to $date (including $date).
	def lowestUpToDate (self, date, days, field='Close'):
		return self.data.lowestUpToDate(date, days, field)
	
	# Return the highest value in $days up to $date (including $date).
	def highestUpToDate (self, date, days, field='Close'):
		return self.data.highestUpToDate(date, days, field)
	
	# Move to next tick (typically next day), and set acted if in emulation mode 
	# noticing main thread actions have been taken for this tick.
	def moveToNextTick (self, 
		dateSet,
		**extra	#附加参数，仅用于统计数据
		):
		time = dateSet.curDate()
		nextTick = dateSet.getSetNextDate()
		'''
		nextTick为None说明模拟已经结束，无论是Emulation或CTP模式，都不能直接设置acted
		标志，因为这会让主调度进程认为此线程已经完全结束，并立即产生下一个tick，且将运行控
		制块(RunCtrl)分配个下一个等待执行线程。在该等待线程开始执行的时候有可能一部分tick
		已经过去了。这会造成模拟误差。Emulate的run（）方法会进行统一处理。
		'''
		if self.emuRunCtrl is not None :
			#在emulate或CTP模式。
			
			#doStatistics仅仅在交易日结束之后统计利润等数据，对moveToNextTick的工作流程
			#没有任何影响，可以把它当作透明的
			self.doStatistics(time, extra['price'], extra['direction'])
			
			if nextTick is not None:
				#对历史数据的模拟未结束，设置acted标志等待主线程调度
				self.emuRunCtrl.setActed()
			elif self.ctpPos is not None:
				'''
				从dataSet返回的下一tick为None说明模拟阶段已经结束，转入实盘阶段。
				'''
				#至此打开窗口终端显示，任何行情相关信息应立即显示。
				self.paintLogOn = True
				
				firstTime = True
				#实盘开关未开启说明交易启动时间未到
				while self.ctpPosOn == False:
					if firstTime == True:
						self.log('Waiting till start time %s' % (self.startTime))
						firstTime = False
					'''
					如果行情服务器时间已大于启动时间则启动持仓管理接口，开始工作，
					否则一直等待。
					'''
					updateTime = strptime(self.data.getUpdateTime(), '%H:%M:%S')
					startTime = strptime(self.startTime, '%H:%M:%S')
					if updateTime >= startTime:
						self.ctpPosOn = True	#实盘开平仓
						self.log('Tracing signals...')
					
					sleep(1)	#每过1秒检查一次启动时间
				
				'''
				1，启动时间到，开始工作。
				2，设置下一tick为当前，避免执行结束。
				3，并每过0.5秒重新察看一次交易信号。
				'''
				nextTick = self.workDay
				sleep(0.5)
				
		return nextTick
		
	#是否有剩余仓位可用
	def positionAvailable (self):
		#是否已达合约最高持仓上限
		if self.curPostion() >= self.maxAddPos:
			return False
		
		#是否已达市场最高持仓上限
		if self.emuRunCtrl and self.emuRunCtrl.marRunStat:
			if self.emuRunCtrl.marRunStat.fullPositions():
				#self.log("	@-.-@ Market max allowed positions are full!")
				return False
		
		#两者均未满，返回
		return True
		