#!/usr/bin/python

'''
This is the core framework to manage all records in Time field for a data table.

Fetch all Time records from a data table at initialization, then directly use them 
without accesssing database again and again, this brings convenience and improves 
performance.
'''

import db.mysqldb as sql

class Date:
	def __init__ (self, database, table):
		self.db = sql.MYSQL("localhost", 'win', 'winfwinf', database)
		self.db.connect()
		self.fillDates(table)
		return
	
	def __exit__ (self):
		self.db.close()
		return
	
	# Fill dateset using the records stored in Time field of a data table.
	def fillDates (self, table):
		sqls = 'select Time from %s order by %s asc' % (table, 'Time')
		#self.db.search(table, None, 'Day')
		self.db.execSql(sqls)
		self.dateSet = self.db.fetch('all')
		self.dateIndex = 0
		self.indexBound = len(self.dateSet)
		#print self.indexBound
		#print self.dateSet
		return
	
	# Transfer a date value to a string.
	def _dateToString (self, date):
		retDate = '%s' % date
		return retDate
	
	# Return the current date referred by current index in dateset.
	def curDate (self):
		if self.dateIndex >= 0 and self.dateIndex < self.indexBound:
			return self._dateToString(self.dateSet[self.dateIndex][0])
		return None
	
	# Return the first date in dateset.
	def firstDate (self):
		return self._dateToString(self.dateSet[0][0])
	
	# Return the last date in dateset.
	def lastDate (self):
		return self._dateToString(self.dateSet[self.indexBound-1][0])
	
	# Return if @date is the first date in dateset.
	def isFirstDate (self, date):
		if self._dateToString(self.dateSet[0][0]) == date:
			return True
		else:
			return False
	
	# Return if @date is the last date in dateset.
	def isLastDate (self, date):
		if self._dateToString(self.dateSet[self.indexBound-1][0]) == date:
			return True
		else:
			return False
	
	# Return the next date behind passed @date.
	def nextDate (self, date):
		i = 0
		while i < self.indexBound:
			if self._dateToString(self.dateSet[i][0]) == date:
				if i+1 < self.indexBound:
					return self._dateToString(self.dateSet[i+1][0])
				else:
					return None
			i = i + 1

		return None
	
	# Return the previous date before passed @date.
	def prevDate (self, date):
		i = 0
		while i < self.indexBound:
			if self._dateToString(self.dateSet[i][0]) == date:
				if i-1 >= 0:
					return self._dateToString(self.dateSet[i-1][0])
				else:
					return None	
			i = i + 1

		return None
		
	# Set @date as current date.
	def setCurDate (self, date):
		#print date
		#time = '%s' % (self.dateSet[0][0])
		#print time
		i = 0
		while i < self.indexBound:
			if self._dateToString(self.dateSet[i][0]) == date:
				self.dateIndex = i
				return i
			i = i + 1
			
		return None
	
	# Return current date and set next date as current date.
	def getSetNextDate (self):
		if self.dateIndex + 1 < self.indexBound:
			self.dateIndex = self.dateIndex + 1
			return self._dateToString(self.dateSet[self.dateIndex][0])
		else:
			return None
	
	# Return current date and set previous date as current date.
	def getSetPrevDate (self):
		if self.dateIndex - 1 >= 0:
			self.dateIndex = self.dateIndex - 1
			return self._dateToString(self.dateSet[self.dateIndex][0])
		else:
			return None
	
	# Get the date behind @date by @days days.
	def getDateNextDays (self, date, days):
		i = 0
		retDate = None
		while i < self.indexBound:
			if self._dateToString(self.dateSet[i][0]) == date:
				if i + days < self.indexBound:
					retDate =  self._dateToString(self.dateSet[i+days][0])
				break
			elif self._dateToString(self.dateSet[i][0]) > date:
				if i + days - 1 < self.indexBound:
					retDate =  self._dateToString(self.dateSet[i + days - 1][0])
				break
			i += 1

		return retDate
			
	# Get the date before @date by @days days.
	def getDatePrevDays (self, date, days):
		i = self.indexBound - 1
		retDate = None
		while i >= 0:
			if self._dateToString(self.dateSet[i][0]) == date:
				if i - days >= 0:
					retDate =  self._dateToString(self.dateSet[i-days][0])
				break
			elif self._dateToString(self.dateSet[i][0]) < date:
				if i - days + 1 >= 0:
					retDate =  self._dateToString(self.dateSet[i - days + 1][0])
				break
			i -= 1

		return retDate
		