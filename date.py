#!/usr/bin/python

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
	
	def _dateToString (self, date):
		retDate = '%s' % date
		return retDate
	
	def curDate (self):
		if self.dateIndex >= 0 and self.dateIndex < self.indexBound:
			return self._dateToString(self.dateSet[self.dateIndex][0])
		return None
	
	def firstDate (self):
		return self._dateToString(self.dateSet[0][0])
	
	def lastDate (self):
		return self._dateToString(self.dateSet[self.indexBound-1][0])
	
	def isFirstDate (self, date):
		if self._dateToString(self.dateSet[0][0]) == date:
			return True
		else:
			return False
	
	def isLastDate (self, date):
		if self._dateToString(self.dateSet[self.indexBound-1][0]) == date:
			return True
		else:
			return False
	
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
	
	def getSetNextDate (self):
		if self.dateIndex + 1 < self.indexBound:
			self.dateIndex = self.dateIndex + 1
			return self._dateToString(self.dateSet[self.dateIndex][0])
		else:
			return None
	
	def getSetPrevDate (self):
		if self.dateIndex - 1 >= 0:
			self.dateIndex = self.dateIndex - 1
			return self._dateToString(self.dateSet[self.dateIndex][0])
		else:
			return None
	
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
		