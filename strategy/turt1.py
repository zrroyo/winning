#! /usr/bin/python

import sys
sys.path.append("..")

import date as DATE
import turtle
import futcom
import db.mysqldb as sql

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
	
	def hitShortSignal (self, date, price):
		#if self.data.getClose(date) < self.lowestBeforeDate(date, 20, 'Lowest'):
		if price < self.lowestBeforeDate(date, 20):
			print "%s Hit Short Signal: Close %s, Lowest %s" % (date, price, self.lowestBeforeDate(date, 20))
			return True
		return False
			
	def hitLongSignal (self, date, price):
		#if self.data.getClose(date) > self.highestBeforeDate(date, 20, 'Highest'):
		if price > self.highestBeforeDate(date, 20):
			print "%s Hit Long Signal: (Close %s), (Highest %s)" % (date, price, self.highestBeforeDate(date, 20))
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
			
			if pLastAddPrice - price >= self.minPosIntv:
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
				
			if price - pLastAddPrice >= self.minPosIntv:
				if self.curPostion() < self.maxPos:
					self.openLongPostion(price)
					print "	[Long] [%s] add postion	last add %s,  close %s, intv %d" % (time, pLastAddPrice, price, price-pLastAddPrice)
					pLastAddPrice = price
					cutLossMode = False
					pLimitByM10 = 0
						
			time = dateSet.getSetNextDate()
				
		return time
	
	def _simulation (self, extra):
		print '\n	<<<<<<<<<<< Turt1 simulation on %s >>>>>>>>>>>	' % self.futName
		
		extra = extra.split(',')
		if len(extra) < 6:
			print "\nTurt1 assistant requires extra imformation specified by '-e' with format 'date,price,maxPos,minPos,minPosIntv,priceUnit'.\n"
			return
			
		table = self.dataTable
		date = extra[0]
		price = int(extra[1])
		
		db = sql.MYSQL("localhost", 'win', 'winfwinf', self.database)
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
		
		maxPos = int(extra[2])
		minPos = int(extra[3])
		minPosIntv = int(extra[4])
		priceUnit = int(extra[5])
		
		self.setAttrs(maxPos, minPos, minPosIntv, priceUnit)
		self.run()
		
		cond = 'Time = "%s"' % date
		db.remove(table, cond)
		db.close()
		
	def assistant (self, extra):
		#extra = extra.split(',')
		#if len(extra) < 3:
			#print "\nTurt1 assistant requires extra imformation specified by '-e' with format 'table,date,price'.\n"
			#return
			
		#table = futcom.futcodeToDataTable(extra[0])
		#date = extra[1]
		#price = int(extra[2])
		
		#if self.hitShortSignal(date, price):
			#print "\n	Turt1: Hit [Short] signal!.\n"
		#elif self.hitLongSignal(date, price):
			#print "\n	Turt1: Hit [Long] signal!.\n"
		#else:
			#print "\n	Turt1: No condition matched. Do nothing\n"
			
		self._simulation(extra)
			
	