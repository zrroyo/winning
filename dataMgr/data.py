#! /usr/bin/python

import sys
sys.path.append("..")
import db.mysqldb as sql

class Data:
	def __init__ (self, database, table):
		self.db = sql.MYSQL("localhost", 'win', 'winfwinf', database)
		self.table = table
		self.db.connect()
		return
	
	def __exit__ (self):
		self.db.close()
		return 
	
	def sum (self, data):
		i = 0
		sum = 0
		#print data[0], data[0][0], len(data)

		while i < len(data):
			sum = sum + data[i][0]
			i = i + 1
			
		return sum

	def avg (self, data, count):
		return self.sum(data) / count
	
	def M (self, date, field='Close', days=1):
		cond = 'Time <= "%s" order by Time desc limit %d' % (date, days)
		#print cond
		num = self.db.search(self.table, cond, field)
		res = self.db.fetch('all')
		#print res
		#print res[0][0]

		return self.avg(res, num)
		
		#sqls = 'select sum(%s)/%s from (select * from %s where Time <= "%s" order by Time desc limit %s) as t1' % (filed, days, self.table, date, days)
		
		#self.db.execSql(sqls)
		#res = self.db.fetch()
		#return res[0]
	
	def M5 (self, date, field='Close'):
		return self.M(date, field, 5)
	
	def M10 (self, date, field='Close'):
		return self.M(date, field, 10)
	
	def M20 (self, date, field='Close'):
		return self.M(date, field, 20)
	
	def M40 (self, date, field='Close'):
		return self.M(date, field, 40)
	
	def M60 (self, date, field='Close'):
		return self.M(date, field, 60)
	
	def getOpen (self, date):
		return self.M(date, 'Open', 1)
	
	def getClose (self, date):
		return self.M(date, 'Close', 1)
	
	def getHighest (self, date):
		return self.M(date, 'Highest', 1)
	
	def getLowest (self, date):
		return self.M(date, 'Lowest', 1)
	
	# Return the lowest value in $days (excluding $date) before $date.
	def lowestBeforeDate (self, date, days, field='Close'):
		sqls = """select min(%s) from (select %s from %s where Time < \'%s\' 
		order by Time desc limit %d) as t1""" % (field, field, self.table, date, days-1)
		
		#print sqls
		
		if self.db.execSql(sqls):
			return self.db.fetch(0)[0];
		return None
	
	# Return the highest value in $days (excluding $date) before $date.
	def highestBeforeDate (self, date, days, field='Close'):
		sqls = """select max(%s) from (select %s from %s where Time < \'%s\' 
		order by Time desc limit %d) as t1""" % (field, field, self.table, date, days-1)
		
		#print sqls
		
		if self.db.execSql(sqls):
			return self.db.fetch(0)[0];
		
		return None
		
	# Return the lowest value in $days up to $date (including $date).
	def lowestUpToDate (self, date, days, field='Close'):
		sqls = """select min(%s) from (select %s from %s where Time <= \'%s\' 
		order by Time desc limit %d) as t1""" % (field, field, self.table, date, days)
		
		#print sqls
		
		if self.db.execSql(sqls):
			return self.db.fetch(0)[0];
		return None

	# Return the highest value in $days up to $date (including $date).
	def highestUpToDate (self, date, days, field='Close'):
		sqls = """select max(%s) from (select %s from %s where Time <= \'%s\' 
		order by Time desc limit %d) as t1""" % (field, field, self.table, date, days)
		
		#print sqls
		
		if self.db.execSql(sqls):
			return self.db.fetch(0)[0];
		
		return None
	