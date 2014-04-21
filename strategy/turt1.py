#-*- coding:utf-8 -*-

import sys
sys.path.append("..")

from date import *
from turtle import *
from db.mysqldb import *
from time import sleep

class Turt1(Turtle):
	
	stableTriggerCount = 3	#可判断为稳定的连续触发次数
	
	def __init__ (self, 
		futName, 
		dataTable, 
		tradeTable, 
		database='futures', 
		runStat=None,
		):
		# Inherit all public methods and attributes from Turtle Class.
		Turtle.__init__(self, futName, dataTable, tradeTable, database, runStat)
		
	def hitShortSignal (self, 
		date,	#交易日
		price,	#待判定价格
		):
		if self.stableLowestInPastDays(price, date, 20):
			if self.workMode == 'atr':
				minPosIntv = self.turtData.getAtr(date) / 2
			else:
				minPosIntv = self.minPosIntv
			
			self.log("%s Hit Short Signal: Close %s, Lowest %s, minPosIntv %d" % (date, price, self.data.lowestBeforeDate(date, 20), minPosIntv))
			return True
			
		return False
			
	def hitLongSignal (self, 
		date,	#交易日
		price,	#待判定价格
		):
		if self.stableHighestInPastDays(price, date, 20):
			if self.workMode == 'atr':
				minPosIntv = self.turtData.getAtr(date) / 2
			else:
				minPosIntv = self.minPosIntv
				
			self.log("%s Hit Long Signal: Close %s, Highest %s, minPosIntv %d" % (date, price, self.data.highestBeforeDate(date, 20), minPosIntv))
			return True
			
		return False
		
	#是否稳定为过去几天内最高值
	def stableHighestInPastDays (self, 
		price,	#待判断价格
		time, 	#交易日
		days	#指定判断天数
		):
		'''
		对于非CTP模式或CTP模式的拟合阶段，数据均来源于本地，都是稳定的。
		'''
		if self.ctpPosOn == False:
			if price > self.data.highestBeforeDate(time, days):
				return True
			else:
				return False
		
		'''
		在实盘阶段，如果连续指定次价格均为指定天数内最高价，则判定为稳定并返回真，否则为假。
		'''
		count = 0
		while price > self.data.highestBeforeDate(time, days):
			self.log("Matching stable highest in past %d days, price %d, count %d" % (days, price, count))
			if count < self.stableTriggerCount:
				sleep(1)
				count += 1
				price = self.data.getClose(time)
				continue
				
			return True
				
		return False
		
	#是否稳定为过去几天内最低值
	def stableLowestInPastDays (self, 
		price,	#待判断价格
		time, 	#交易日
		days	#指定判断天数
		):
		'''
		对于非CTP模式或CTP模式的拟合阶段，数据均来源于本地，都是稳定的。
		'''
		if self.ctpPosOn == False:
			if price < self.data.lowestBeforeDate(time, days):
				return True
			else:
				return False
		
		'''
		在实盘阶段，如果连续指定次价格均为指定天数内最低价，则判定为稳定并返回真，否则为假。
		'''
		count = 0
		while price < self.data.lowestBeforeDate(time, days):
			self.log("Matching stable lowest in past %d days, price %d, count %d" % (days, price, count))
			if count < self.stableTriggerCount:
				sleep(1)
				count += 1
				price = self.data.getClose(time)
				continue
				
			return True
				
		return False
		
	#是否稳定高于M10
	def stableHigherThanM10 (self, 
		price,	#待判断价格
		time, 	#交易日
		):
		'''
		对于非CTP模式或CTP模式的拟合阶段，数据均来源于本地，都是稳定的。
		'''
		if self.ctpPosOn == False:
			if price > self.data.M10(time):
				return True
			else:
				return False
		
		'''
		在实盘阶段，如果连续指定次价格均高于M10，则判定为稳定并返回真，否则为假。
		'''
		count = 0
		while price > self.data.M10(time):
			self.log("Matching stable higher than M10, price %d, count %d" % (price, count))
			if count < self.stableTriggerCount:
				sleep(1)
				count += 1
				price = self.data.getClose(time)
				continue
				
			return True
				
		return False
		
	#是否稳定低于M10
	def stableLowerThanM10 (self, 
		price,	#待判断价格
		time, 	#交易日
		):
		'''
		对于非CTP模式或CTP模式的拟合阶段，数据均来源于本地，都是稳定的。
		'''
		if self.ctpPosOn == False:
			if price < self.data.M10(time):
				return True
			else:
				return False
		
		'''
		在实盘阶段，如果连续指定次价格均低于M10，则判定为稳定并返回真，否则为假。
		'''
		count = 0
		while price < self.data.M10(time):
			self.log("Matching stable lower than M10, price %d, count %d" % (price, count))
			if count < self.stableTriggerCount:
				sleep(1)
				count += 1
				price = self.data.getClose(time)
				continue
				
			return True
				
		return False
		
	#是否稳定满足加空仓条件
	def stableToAddShortPosition (self, 
		time,		#交易日
		pLastAddPrice,	#上一次加仓价格
		price,		#待判断价格
		minPosIntv, 	#加仓间断值
		):
		'''
		对于非CTP模式或CTP模式的拟合阶段，数据均来源于本地，都是稳定的。
		'''
		if self.ctpPosOn == False:
			if pLastAddPrice - price >= minPosIntv:
				return True
			else:
				return False
			
		#已经满仓，直接返回。
		if not self.positionAvailable():
			return False
			
		'''
		在实盘阶段，如果连续指定次价格均条件为真，则判定为稳定并返回真，否则为假。
		'''
		count = 0
		while pLastAddPrice - price >= minPosIntv:
			self.log("Matching stable to add short position, price %d, count %d" % (price, count))
			if count < self.stableTriggerCount:
				sleep(1)
				count += 1
				price = self.data.getClose(time)
				continue
				
			return True
				
		return False
		
	#是否稳定满足加多仓条件
	def stableToAddLongPosition (self, 
		time,		#交易日
		pLastAddPrice,	#上一次加仓价格
		price,		#待判断价格
		minPosIntv, 	#加仓间断值
		):
		'''
		对于非CTP模式或CTP模式的拟合阶段，数据均来源于本地，都是稳定的。
		'''
		if self.ctpPosOn == False:
			if price - pLastAddPrice >= minPosIntv:
				return True
			else:
				return False
			
		#已经满仓，直接返回。
		if not self.positionAvailable():
			return False
			
		'''
		在实盘阶段，如果连续指定次价格均条件为真，则判定为稳定并返回真，否则为假。
		'''
		count = 0
		while price - pLastAddPrice >= minPosIntv:
			self.log("Matching stable to add long position, price %d, count %d" % (price, count))
			if count < self.stableTriggerCount:
				sleep(1)
				count += 1
				price = self.data.getClose(time)
				continue
				
			return True
				
		return False
		
	#做空
	def doShort (self, 
		dateSet,	#时间集
		date,		#开始日期
		):
		days = 0
		self.emptyPostion()
		pLastAddPrice = self.openShortPosition(self.data.getClose(date))
		cutLossMode = False
		pLimitByM10 = 0
		time = self.moveToNextTick(dateSet,
				price = self.data.getClose(date),
				direction = 'short')
				
		if self.workMode == 'atr':
			minPosIntv = self.turtData.getAtr(date) / 2
		else:
			minPosIntv = self.minPosIntv
		
		while time is not None:
			if self.emuRunCtrl is not None:
				tickReady = self.emuRunCtrl.tickIsReady(time, self, direction = 'short')
				if tickReady is 'False':
					continue
				
			days = days + 1
			price = self.data.getClose(time)
			
			if self.stableHighestInPastDays(price, time, 10):
				price = self.closeAllPostion(price, 'short')
				self.log("	[Short] [%s] Hit Highest in 10 days: Clear all! %d days:	open %s,  close %s, highest %d" % (time, days, self.data.getClose(date), price, self.data.highestBeforeDate(time, 10)))
				#time = dateSet.getSetNextDate()
				break
				
			if not (cutLossMode or self.curPostion() == 1) and self.stableHigherThanM10(price, time):
				cutLossMode = True
				pLimitByM10 = self.data.lowestBeforeDate(time, 5)
				
				mult = self.curPostion()*2/3
				if mult == 0:
					mult = 1
					
				price = self.closeMultPostion(mult, price, 'short')
				
				self.log("	[Short] [%s] M10 BT lasted %d days:	open %s,  close %s, M10 %s, mult %d, pLimitByM10 %d" % (time, days, pLastAddPrice, price, self.data.M10(time), mult, pLimitByM10))
				
				if self.curPostion() == 0:
					break
				time = self.moveToNextTick(dateSet, 
							price = self.data.getClose(time), 
							direction = 'short'
							)
				continue
			
			if cutLossMode and price >= pLimitByM10:
				time = self.moveToNextTick(dateSet, 
							price = self.data.getClose(time), 
							direction = 'short'
							)
				continue
			
			if self.stableToAddShortPosition(time, pLastAddPrice, price, minPosIntv):
				if self.curPostion() < self.maxAddPos:
					price = self.openShortPosition(price)
					if price is not None:
						self.log("	[Short] [%s] add postion	last add %s,  close %s, intv %d" % (time, pLastAddPrice, price, pLastAddPrice-price))
						pLastAddPrice = price
						cutLossMode = False
						pLimitByM10 = 0
				
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
		cutLossMode = False
		pLimitByM10 = 0
		time = self.moveToNextTick(dateSet,
				price = self.data.getClose(date), 
				direction = 'long')
		
		if self.workMode == 'atr':
			minPosIntv = self.turtData.getAtr(date) / 2
		else:
			minPosIntv = self.minPosIntv
			
		while time is not None:
			if self.emuRunCtrl is not None:
				tickReady = self.emuRunCtrl.tickIsReady(time, self, direction = 'long')
				if tickReady is 'False':
					continue
					
			days = days + 1
			price = self.data.getClose(time)
			
			if self.stableLowestInPastDays(price, time, 10):
				price = self.closeAllPostion(price, 'long')
				self.log("	[Long] [%s] Hit Lowest in 10 days: Clear all! %d days:	open %s,  close %s, lowest %d" % (time, days, self.data.getClose(date), price, self.data.lowestBeforeDate(time, 10)))
				#time = dateSet.getSetNextDate()
				break
				
			if  not (cutLossMode or self.curPostion() == 1) and self.stableLowerThanM10(price, time):
				cutLossMode = True
				pLimitByM10 = self.data.highestBeforeDate(time, 5)
					
				mult = self.curPostion()*2/3
				if mult == 0:
					mult = 1
					
				price = self.closeMultPostion(mult, price, 'long')
				
				self.log("	[Long] [%s] M10 BT lasted %d days:	open %s,  close %s, M10 %s, mult %d, pLimitByM10 %d" % (time, days, pLastAddPrice, price, self.data.M10(time), mult, pLimitByM10))
				
				if self.curPostion() == 0:
					break
				time = self.moveToNextTick(dateSet, 
							price = self.data.getClose(time), 
							direction = 'long'
							)
				continue
				
			if cutLossMode and price <= pLimitByM10:
				time = self.moveToNextTick(dateSet, 
							price = self.data.getClose(time), 
							direction = 'long'
							)
				continue
				
			if self.stableToAddLongPosition(time, pLastAddPrice, price, minPosIntv):
				if self.curPostion() < self.maxAddPos:
					price = self.openLongPosition(price)
					if price is not None:
						self.log("	[Long] [%s] add postion	last add %s,  close %s, intv %d" % (time, pLastAddPrice, price, price-pLastAddPrice))
						pLastAddPrice = price
						cutLossMode = False
						pLimitByM10 = 0
						
			time = self.moveToNextTick(dateSet, 
						price = self.data.getClose(time), 
						direction = 'long'
						)
				
		return time
	
	def _simulation (self, extra):
		print '\n	<<<<<<<<<<< Turt1 simulation on %s >>>>>>>>>>>	' % self.futName
		
		extra = extra.split(',')
		if len(extra) < 6:
			print "\nTurt1 assistant requires extra imformation specified by '-e' with format 'date,price,maxAddPos,minPos,minPosIntv(or ''),priceUnit'.\n"
			return
			
		table = self.dataTable
		date = extra[0]
		price = int(extra[1])
		
		db = MYSQL("localhost", 'win', 'winfwinf', self.database)
		db.connect()
		
		if db.ifRecordExist(table, 'Time', date):
			print "\nData record with Time '%s' exists in '%s', simulation may break data table, exit...\n" % (date, table)
			db.close()
			return
		else:
			values = values = '"%s", 0, 0, 0, %s, 0, 0, 0, Null, Null' % (date, price)
			db.insert(table, values)
			
		# Add new record, need sync dateSet.
		self.dateSet.fillDates(table)
		
		maxAddPos = int(extra[2])
		minPos = int(extra[3])
		minPosIntv = int(extra[4])
		priceUnit = int(extra[5])
		
		self.setAttrs(maxAddPos, minPos, minPosIntv, priceUnit)
		self.run()
		
		cond = 'Time = "%s"' % date
		db.remove(table, cond)
		db.close()
		
	def assistant (self, extra):
		self._simulation(extra)
			
	