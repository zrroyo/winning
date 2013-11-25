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
	
	def setAttrs (self, maxAddPos, minPos, minPosIntv, priceUnit):
		self.maxAddPos = maxAddPos
		self.minPos = minPos
		self.minPosIntv = minPosIntv
		self.priceUnit = priceUnit
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
			self.closeAllPostion(price, mode)
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
	
				time = self.moveToNextTick(lcDateSet)
				
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
	def moveToNextTick (self, dateSet):
		nextTick = dateSet.getSetNextDate()
		# Note, if nextTick is None (the end of emulation), we do not set acted flag because 
		# it may leave chance for main thread to generate next tick possibly causing missing
		# some workable ticks.
		if self.emuRunCtrl is not None :
			#在emulate或CTP模式。
			if nextTick is not None:
				#在数据表中的模拟未结束，设置acted标志等待主线程调度
				self.emuRunCtrl.setActed()
			elif self.ctpPos is not None:
				'''
				在CTP模式，已经结束对过去数据的拟合并转入当前交易日，应进行实盘交易。
				设置下一tick为当前，避免执行结束。
				'''
				nextTick = self.workDay	
				self.paintLogOn = True	#开始用终端窗口显示log
				
				'''
				如果行情服务器时间已大于启动时间则启动持仓管理接口开始工作，否则一直等待。
				'''
				updateTime = strptime(self.data.getUpdateTime(), '%H:%M:%S')
				startTime = strptime(self.startTime, '%H:%M:%S')
				if updateTime >= startTime:
					self.ctpPosOn = True	#实盘开平仓
					self.log('%d, tracing, move to next tick...' % (self.data.getClose(nextTick)))
				else:
					self.log('wait utill start time %s' % (self.startTime))
				
				sleep(0.5)
				
		return nextTick
	