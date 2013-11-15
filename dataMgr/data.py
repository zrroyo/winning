#-*- coding:utf-8 -*-

import sys
sys.path.append("..")
import time
import db.mysqldb as sql
from ctp.ctpagent import MarketDataAgent

#数据库数据对象
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
	
#CTP数据对象
class CtpData(Data):
	def __init__ (self, 
		instrument, 	#合约号
		database, 	#存储数据库名
		table, 		#数据库中的数据表
		workDay,	#工作日,必须以'%Y-%m-%d'格式
		mdagent		#行情数据代理
		):
		Data.__init__(self, database, table)
		self.workDay = workDay
		self.mdlocal = mdagent.mdlocal
		
	def __isPastDate (self, date):
		t1 = time.strptime(date, '%Y-%m-%d')
		t2 = time.strptime(self.workDay, '%Y-%m-%d')
		
		if t1 < t2:
			return True
		elif t1 == t2:
			return False
		else:
			print 'CtpData: Bad date'
			return False
			
	def ctp_M (self, date, field='Close', days=1):
	
	def getOpen (self, date):
		if self.__isPastDate(date):
			return self.M(date, 'Open', 1)
		else:
			return self.mdlocal.getOpen(self.instrument)
		
	def getClose (self, date):
		if self.__isPastDate(date):
			return self.M(date, 'Close', 1)
		else:
			return self.mdlocal.getClose(self.instrument)
			
	def getHighest (self, date):
		if self.__isPastDate(date):
			return self.M(date, 'Highest', 1)
		else:
			return self.mdlocal.getHighest(self.instrument)
			
	def getLowest (self, date):
		if self.__isPastDate(date):
			return self.M(date, 'Lowest', 1)
		else:
			return self.mdlocal.getLowest(self.instrument)
				