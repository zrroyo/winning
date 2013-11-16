#-*- coding:utf-8 -*-

import sys
sys.path.append("..")
import time
import db.mysqldb as sql
#from ctp.ctpagent import MarketDataAgent

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
	
	def M30 (self, date, field='Close'):
		return self.M(date, field, 30)
	
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
		self.instrument = instrument
		self.workDay = workDay
		self.mdlocal = mdagent.mdlocal
		
	#判断是否是已过去的交易日
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
			
	#计算当前交易日的移动均线值
	def ctp_M (self, date, field='Close', days=1):
		'''
		CTP的当前时间必然要大于数据库中所存储的最大时间，
		数据库中存储的为过去的数据，而CTP中的为当前数据。
		'''
		cond = 'Time < "%s" order by Time desc limit %d' % (date, days-1)
		#print cond
		num = self.db.search(self.table, cond, field)
		res = self.db.fetch('all')
		#print res
		#print res[0][0]
		
		if field == 'Close':
			value = self.mdlocal.getClose(self.instrument)
		elif field == 'Open':
			value = self.mdlocal.getOpen(self.instrument)
		elif field == 'Highest':
			value = self.mdlocal.getHighest(self.instrument)
		elif field == 'Lowest':
			value = self.mdlocal.getLowest(self.instrument)
				
		return (self.sum(res) + value) / (num + 1)
		
	#5日移动均线
	def M5 (self, date, field='Close'):
		if self.__isPastDate(date):
			return self.M(date, field, 5)
		else:
			return self.ctp_M(date, field, 5)
			
	#10日移动均线
	def M10 (self, date, field='Close'):
		#print self.__isPastDate(date)
		if self.__isPastDate(date):
			return self.M(date, field, 10)
		else:
			return self.ctp_M(date, field, 10)
	
	#20日移动均线
	def M20 (self, date, field='Close'):
		if self.__isPastDate(date):
			return self.M(date, field, 20)
		else:
			return self.ctp_M(date, field, 20)
			
	#30日移动均线
	def M30 (self, date, field='Close'):
		if self.__isPastDate(date):
			return self.M(date, field, 30)
		else:
			return self.ctp_M(date, field, 30)
			
	#60日移动均线
	def M60 (self, date, field='Close'):
		if self.__isPastDate(date):
			return self.M(date, field, 60)
		else:
			return self.ctp_M(date, field, 60)
			
	#得到开盘价
	def getOpen (self, date):
		if self.__isPastDate(date):
			return self.M(date, 'Open', 1)
		else:
			return self.mdlocal.getOpen(self.instrument)
		
	#得到收盘价
	def getClose (self, date):
		if self.__isPastDate(date):
			return self.M(date, 'Close', 1)
		else:
			return self.mdlocal.getClose(self.instrument)
			
	#得到最高价
	def getHighest (self, date):
		if self.__isPastDate(date):
			return self.M(date, 'Highest', 1)
		else:
			return self.mdlocal.getHighest(self.instrument)
			
	#得到最低价
	def getLowest (self, date):
		if self.__isPastDate(date):
			return self.M(date, 'Lowest', 1)
		else:
			return self.mdlocal.getLowest(self.instrument)
			
	#得到包含当前交易日的数天内的最低价
	def lowestUpToDate (self, date, days, field='Close'):
		if self.__isPastDate(date):
			return Data.lowestUpToDate(self, date, days, field)
		
		lowest = Data.lowestBeforeDate(self, date, days, field)
		
		if field == 'Close':
			value = self.mdlocal.getClose(self.instrument)
		elif field == 'Open':
			value = self.mdlocal.getOpen(self.instrument)
		elif field == 'Highest':
			value = self.mdlocal.getHighest(self.instrument)
		elif field == 'Lowest':
			value = self.mdlocal.getLowest(self.instrument)
			
		return min(lowest, value)
		
	#得到包含当前交易日的数天内的最高价
	def highestUpToDate (self, date, days, field='Close'):
		if self.__isPastDate(date):
			return Data.highestUpToDate(self, date, days, field)
		
		highest = Data.highestUpToDate(self, date, days, field)
		
		if field == 'Close':
			value = self.mdlocal.getClose(self.instrument)
		elif field == 'Open':
			value = self.mdlocal.getOpen(self.instrument)
		elif field == 'Highest':
			value = self.mdlocal.getHighest(self.instrument)
		elif field == 'Lowest':
			value = self.mdlocal.getLowest(self.instrument)
			
		return max(highest, value)
			