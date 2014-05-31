#-*- coding:utf-8 -*-

from turt1 import *

#
class DevStr (Turt1):
	def __init__ (self, futName, dataTable, tradeTable, database='futures', runStat=None):
		Turt1.__init__(self, futName, dataTable, tradeTable, database, runStat)
	
	#做空
	def doShort (self, 
		dateSet,	#时间集
		date,		#开始日期
		):
		days = 0
		self.emptyPostion()
		pLastAddPrice = self.openShortPosition(self.data.getClose(date))
		time = self.moveToNextTick(dateSet,
				price = self.data.getClose(date),
				direction = 'short')
	
		minPosIntv = self.minPosIntv

		while time is not None:
			days = days + 1
			price = self.data.getClose(time)
			
			if self.stableHighestInPastDays(price, time, 10):
				price = self.closeAllPostion(price, 'short')
				self.log("	[Short] [%s] Hit Highest in 10 days: Clear all! %d days:	open %s,  close %s, highest %d" % (time, days, self.data.getClose(date), price, self.data.highestBeforeDate(time, 10)))
				#time = dateSet.getSetNextDate()
				self.doStatistics(time, price, 'short', 'RunStat')
				self.runStat.regress.devStatAssist(self.profit)
				break
				
			if self.stableToAddShortPosition(time, pLastAddPrice, price, minPosIntv):
				if self.curPostion() < self.maxAddPos:
					price = self.openShortPosition(price)
					if price is not None:
						self.log("	[Short] [%s] add postion	last add %s,  close %s, intv %d" % (time, pLastAddPrice, price, pLastAddPrice-price))
						pLastAddPrice = price
				
			time = self.moveToNextTick(dateSet, 
						price = self.data.getClose(time), 
						direction = 'short'
						)
				
		return time
		
	#做多
	def doLong (self, 
		dateSet,	#时间集
		date,		#开始日期
		):
		days = 0
		self.emptyPostion()
		pLastAddPrice = self.openLongPosition(self.data.getClose(date))
		time = self.moveToNextTick(dateSet,
				price = self.data.getClose(date),
				direction = 'long')
			
		minPosIntv = self.minPosIntv
		
		while time is not None:
			days = days + 1
			price = self.data.getClose(time)
			
			if self.stableLowestInPastDays(price, time, 10):
				price = self.closeAllPostion(price, 'long')
				self.log("	[Long] [%s] Hit Lowest in 10 days: Clear all! %d days:	open %s,  close %s, lowest %d" % (time, days, self.data.getClose(date), price, self.data.lowestBeforeDate(time, 10)))
				#time = dateSet.getSetNextDate()
				self.doStatistics(time, price, 'long', 'RunStat')
				self.runStat.regress.devStatAssist(self.profit)
				break
			
			if self.stableToAddLongPosition(time, pLastAddPrice, price, minPosIntv):
				if self.curPostion() < self.maxAddPos:
					price = self.openLongPosition(price)
					if price is not None:
						self.log("	[Long] [%s] add postion	last add %s,  close %s, intv %d" % (time, pLastAddPrice, price, price-pLastAddPrice))
						pLastAddPrice = price
						
			time = self.moveToNextTick(dateSet, 
						price = self.data.getClose(time), 
						direction = 'long'
						)
				
		return time
	