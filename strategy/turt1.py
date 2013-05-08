#! /usr/bin/python

import sys
sys.path.append("..")

import date as DATE
import turtle

class Turt1(turtle.Turtle):
	def __init__ (self, futName, dataTable, tradeTable, database='futures'):
		# Inherit all public methods and attributes from Turtle Class.
		turtle.Turtle.__init__(self, futName, dataTable, tradeTable, database)
		#self.test = turtle.Turtle.table
		#print self.dataTable, self.tradeTable, self.database
		return
	
	def __exit__ (self):
		turtle.Turtle.__exit__(self)
		return
	
	def hitShortSignal (self, date):
		#if self.data.getClose(date) < self.lowestBeforeDate(date, 20, 'Lowest'):
		if self.data.getClose(date) < self.lowestBeforeDate(date, 20):
			print "%s Hit Short Signal: Close %s, Lowest %s" % (date, self.data.getClose(date), self.lowestBeforeDate(date, 20))
			return True
		return False
			
	def hitLongSignal (self, date):
		#if self.data.getClose(date) > self.highestBeforeDate(date, 20, 'Highest'):
		if self.data.getClose(date) > self.highestBeforeDate(date, 20):
			print "%s Hit Long Signal: (Close %s), (Highest %s)" % (date, self.data.getClose(date), self.highestBeforeDate(date, 20))
			return True
		return False
		
	def doShort (self, dateSet, date):
		days = 0
		self.emptyPostion()
		pLastAddPrice = self.data.getClose(date)
		self.openShortPostion(pLastAddPrice)
		cutLossMode = False
		pLimitByM10 = 0
		time = dateSet.getSetNextDate()
		
		while time is not None:
			days = days + 1
			
			# Cut losses.
			price = self.data.getClose(time)
			#if price > self.data.M20(time):
			if price > self.highestBeforeDate(time, 10):
				self.closeAllPostion(price, 'short')
				print "	[Short] [%s] Hit Highest in 10 days: Clear all! %d days:	open %s,  close %s, highest %d" % (time, days, self.data.getClose(date), price, self.highestBeforeDate(time, 10))
				#time = dateSet.getSetNextDate()
				break
			
			if price > self.data.M10(time):
				if cutLossMode:
					time = dateSet.getSetNextDate()
					continue
				
				if self.curPostion() == 1:
					time = dateSet.getSetNextDate()
					continue
					
				cutLossMode = True
				pLimitByM10 = self.lowestBeforeDate(time, 5)
				
				mult = self.curPostion()*2/3
				if mult == 0:
					mult = 1
					
				self.closeMultPostion(mult, price, 'short')
				
				print "	[Short] [%s] M10 BT lasted %d days:	open %s,  close %s, M10 %s, mult %d, pLimitByM10 %d" % (time, days, pLastAddPrice, price, self.data.M10(time), mult, pLimitByM10)
				
				if self.curPostion() == 0:
					break
				time = dateSet.getSetNextDate()
				continue
			
			if cutLossMode and price >= pLimitByM10:
				time = dateSet.getSetNextDate()
				continue
			
			if pLastAddPrice - price > self.minPosIntv:
				if self.curPostion() < self.maxPos:
					self.openShortPostion(price)
					print "	[Short] [%s] add postion	last add %s,  close %s, intv %d" % (time, pLastAddPrice, price, pLastAddPrice-price)	
					pLastAddPrice = price
					cutLossMode = False
					pLimitByM10 = 0
				
			time = dateSet.getSetNextDate()
		
		return time
		
	def doLong (self, dateSet, date):
		days = 0
		self.emptyPostion()
		pLastAddPrice = self.data.getClose(date)
		self.openLongPostion(pLastAddPrice)
		cutLossMode = False
		pLimitByM10 = 0
		time = dateSet.getSetNextDate()
		
		while time is not None:
			days = days + 1
			
			# Cut losses.
			price = self.data.getClose(time)
			#if price < self.data.M20(time):
			if price < self.lowestBeforeDate(time, 10):
				self.closeAllPostion(price, 'long')
				print "	[Long] [%s] Hit Lowest in 10 days: Clear all! %d days:	open %s,  close %s, lowest %d" % (time, days, self.data.getClose(date), price, self.lowestBeforeDate(time, 10))
				#time = dateSet.getSetNextDate()
				break
			
			if price < self.data.M10(time):
				if cutLossMode:
					time = dateSet.getSetNextDate()
					continue
					
				if self.curPostion() == 1:
					time = dateSet.getSetNextDate()
					continue
				
				cutLossMode = True
				pLimitByM10 = self.highestBeforeDate(time, 5)
					
				mult = self.curPostion()*2/3
				if mult == 0:
					mult = 1
					
				self.closeMultPostion(mult, price, 'long')
				
				print "	[Long] [%s] M10 BT lasted %d days:	open %s,  close %s, M10 %s, mult %d, pLimitByM10 %d" % (time, days, pLastAddPrice, price, self.data.M10(time), mult, pLimitByM10)
				
				if self.curPostion() == 0:
					break
				time = dateSet.getSetNextDate()
				continue
				
			if cutLossMode and price <= pLimitByM10:
				time = dateSet.getSetNextDate()
				continue
				
			if price - pLastAddPrice > self.minPosIntv:
				if self.curPostion() < self.maxPos:
					self.openLongPostion(price)
					print "	[Long] [%s] add postion	last add %s,  close %s, intv %d" % (time, pLastAddPrice, price, price-pLastAddPrice)
					pLastAddPrice = price
					cutLossMode = False
					pLimitByM10 = 0
						
			time = dateSet.getSetNextDate()
				
		return time
	