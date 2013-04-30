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
		#if self.data.getClose(date) < self.lowestByDate(date, 20, 'Lowest'):
		if self.data.getClose(date) < self.lowestByDate(date, 20):
			print "%s Hit Short Signal: Close %s, Lowest %s" % (date, self.data.getClose(date), self.lowestByDate(date, 20, 'Lowest'))
			return True
		return False
			
	def hitLongSignal (self, date):
		#if self.data.getClose(date) > self.highestByDate(date, 20, 'Highest'):
		if self.data.getClose(date) > self.highestByDate(date, 20):
			print "%s Hit Long Signal: (Close %s), (Highest %s)" % (date, self.data.getClose(date), self.highestByDate(date, 20))
			return True
		return False
		
	def doShort (self, dateSet, date):
		days = 0
		time = dateSet.getSetNextDate()
		self.emptyPostion()
		pLastAddPrice = self.data.getClose(date)
		self.openShortPostion(pLastAddPrice)
		
		while time is not None:
			days = days + 1
			
			# Cut losses.
			price = self.data.getClose(time)
			#if price > self.data.M20(time):
			if price > self.highestByDate(time, 10):
				print "	[Short] [%s] M20 BT lasted %d days:	open %s,  close %s" % (time, days, self.data.getClose(date), price)
				self.closeAllPostion(price, 'short')
				time = dateSet.getSetNextDate()
				break
			
			if price > self.data.M10(time):
				if self.curPostion() == 1:
					time = dateSet.getSetNextDate()
					continue
					
				mult = self.curPostion()*2/3
				if mult == 0:
					mult = 1
					
				print "	[Short] [%s] M10 BT lasted %d days:	open %s,  close %s, mult %d" % (time, days, pLastAddPrice, price, mult)
				
				self.closeMultPostion(mult, price, 'short')
				
				if self.curPostion() == 0:
					break
				time = dateSet.getSetNextDate()
				continue
				
			if pLastAddPrice - price > self.minPosIntv:
				if self.curPostion() < self.maxPos:
					pos1 = self.curPostion()
					pos2 = self.openShortPostion(price)
					if pos2 > pos1:
						print "	[Short] [%s] add postion	last add %s,  close %s, intv %d" % (time, pLastAddPrice, price, pLastAddPrice-price)	
						pLastAddPrice = price
				
			time = dateSet.getSetNextDate()

	#def doLong (self, dateSet, date):
		#days = 0
		#time = date
		#while time is not None:
			#days = days + 1
			#if self.data.getClose(time) < self.data.M20(time):
				##print "	[Long] [%s] to [%s] lasted %d days:	open %s,  close %s" % (date, time, days, self.data.getClose(date), self.data.getClose(time))
				#break
			#time = dateSet.getSetNextDate()
	
	def doLong (self, dateSet, date):
		days = 0
		time = dateSet.getSetNextDate()
		self.emptyPostion()
		pLastAddPrice = self.data.getClose(date)
		self.openLongPostion(pLastAddPrice)
		
		while time is not None:
			days = days + 1
			
			# Cut losses.
			price = self.data.getClose(time)
			#if price < self.data.M20(time):
			if price < self.lowestByDate(time, 10):
				print "	[Long] [%s] M20 BT lasted %d days:	open %s,  close %s" % (time, days, self.data.getClose(date), price)
				self.closeAllPostion(price, 'long')
				time = dateSet.getSetNextDate()
				break
			
			if price < self.data.M10(time):
				if self.curPostion() == 1:
					time = dateSet.getSetNextDate()
					continue
					
				mult = self.curPostion()*2/3
				if mult == 0:
					mult = 1
					
				print "	[Long] [%s] M10 BT lasted %d days:	open %s,  close %s, mult %d" % (time, days, pLastAddPrice, price, mult)
				
				self.closeMultPostion(mult, price, 'long')
				
				if self.curPostion() == 0:
					break
				time = dateSet.getSetNextDate()
				continue
								
			if price - pLastAddPrice > self.minPosIntv:
				if self.curPostion() < self.maxPos:
					pos1 = self.curPostion()
					pos2 = self.openLongPostion(price)
					if pos2 > pos1:
						print "	[Long] [%s] add postion	last add %s,  close %s, intv %d" % (time, pLastAddPrice, price, price-pLastAddPrice)
						pLastAddPrice = price
						
			time = dateSet.getSetNextDate()
				
