#! /usr/bin/python

import sys
sys.path.append("..")

import dataMgr.data as data 
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


class Turtle(FUT.Futures):
	def __init__ (self, futName, dataTable, tradeTable, database='futures'):
		FUT.Futures.__init__(self, futName)
		self.database = database
		self.dataTable = dataTable
		self.data = data.Data(database, dataTable)
		self.dateSet = DATE.Date(database, dataTable)
		self.tradeTable = tradeTable
		#self.tradeRec = trade.Trade(database, tradeTable)

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
	
	def setAttrs (self, maxPos, minPos, minPosIntv):
		self.maxPos = maxPos
		self.minPos = minPos
		self.minPosIntv = minPosIntv
		return
		
	def checkAttrs (self):
		if self.maxPos is None:
			return False
		elif self.minPos is None:
			return False
		elif self.minPosIntv is None:
			return False
		else:
			return True
	
	def doShort (self, dateSet, date):
		return
		
	def doLong (self, dateSet, date):
		return
	
	def hitShortSignal (self, date):
		return
		
	def hitLongSignal (self, date):
		return
	
	# End of a test run. Close all opened positions before stop test.
	def endRun (self, mode):
		if self.curPostion():
			time = self.dateSet.lastDate()
			price = self.data.getClose(time)
			self.closeAllPostion(price, mode)
			print "	[%s] [%s] Clear all! close %s" % (mode, time, price)
			
		return
		
	def run (self):
		if self.checkAttrs() is False:
			print """
			Key attributss must be set before run strategy, which could be 
			simply made calling setAttrs().
			"""
			return
		
		print '\n\n	<<<<<<<<<<< Run %s >>>>>>>>>>>	\n\n' % self.futName
		
		lcDateSet = DATE.Date(self.database, self.dataTable)
		#lcDateSet = self.dateSet
		time = lcDateSet.firstDate()
		
		days = 0
		mode = None
		
		while time is not None:
			days += 1
			if days <= 10:
				time= lcDateSet.getSetNextDate()
				continue
			
			if self.hitShortSignal(time):
				mode = 'short'
				time = self.doShort(lcDateSet, time);
				# It also possibly hits the Long signal after quit short 
				# mode in same day.
				continue
			elif self.hitLongSignal(time):
				mode = 'long'
				time = self.doLong(lcDateSet, time);
				# It also possibly hits the Short signal after quit long 
				# mode in same day.
				continue
			else:
				mode = None

			time= lcDateSet.getSetNextDate()
			
		if mode is not None:
			self.endRun(mode)
	
	# Get the lowest value for a field within recent $days counted from $date.
	def lowestBeforeDate (self, date, days, field='Close'):
		return self.data.lowestBeforeDate(date, days, field)
		
	# Get the highest value for a field within recent $days counted from $date.
	def highestBeforeDate (self, date, days, field='Close'):
		return self.data.highestBeforeDate(date, days, field)
	
