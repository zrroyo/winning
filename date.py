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
	
	def curDate (self):
		if self.dateIndex >= 0 and self.dateIndex < self.indexBound:
			return self.dateSet[self.dateIndex][0]
		return None
	
	def firstDate (self):
		return self.dateSet[0][0]
	
	def lastDate (self):
		return self.dateSet[self.indexBound-1][0]
	
	def isFirstDate (self, date):
		time = '%s' % (self.dateSet[0][0])
		if time == date:
			return True
		else:
			return False
	
	def isLastDate (self, date):
		time = '%s' % (self.dateSet[self.indexBound-1][0])
		if time == date:
			return True
		else:
			return False
	
	def nextDate (self, date):
		i = 0
		while i < self.indexBound:
			time = '%s' % (self.dateSet[i][0])
			if time == date:
				if i+1 < self.indexBound:
					return self.dateSet[i+1][0]
				else:
					return None
			i = i + 1

		return None
	
	def prevDate (self, date):
		i = 0
		while i < self.indexBound:
			time = '%s' % (self.dateSet[i][0])
			if time == date:
				if i-1 >= 0:
					return self.dateSet[i-1][0]
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
			time = '%s' % (self.dateSet[i][0])
			if time == date:
				self.dateIndex = i
				return i
			i = i + 1
			
		return None
	
	def getSetNextDate (self):
		if self.dateIndex + 1 < self.indexBound:
			self.dateIndex = self.dateIndex + 1
			return self.dateSet[self.dateIndex][0]
		else:
			return None
	
	def getSetPrevDate (self):
		if self.dateIndex - 1 >= 0:
			self.dateIndex = self.dateIndex - 1
			return self.dateSet[self.dateIndex][0]
		else:
			return None
			