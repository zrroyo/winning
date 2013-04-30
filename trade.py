#! /usr/bin/python

import db.mysqldb as sql


class Trade:
	def __init__ (self, database, table):
		self.db = sql.MYSQL("localhost", 'win', 'winfwinf', database)
		self.db.connect()
		self.useTable(table)
		return
	
	def __exit__ (self):
		self.db.close()
		return
	
	def useTable (self, table):
		sqls = 'show tables like "%s"' % table
		res = self.db.execSql(sqls)
		#print res
		if res == 0:
			res = self.createTable(table)
		
		res = self.db.execSql(sqls)
		if res == 1:
			self.table = table
		#print self.table
		return res
	
	def createTable (self, table):
		sqls = """ create table %s (
			Time datetime, Trade varchar(5), Name varchar(10), 
			Type char(4), Ord varchar(50), Price float, Number int, 
			Position float, Margin float, Profit float, Reason varchar(50), 
			Comments varchar(50));
		""" % table
		res = self.db.execSql(sqls)
		res = self.db.attrSetPrimary(table, 'Time')
		#print res
		return res
	
	def __addTrade (self, trade, name, date, ttype, order, price, number, 
		reason=None, profit=0.0, comments=None, postion=0.0, margin=0.0):
		
		if self.table is None:
			return
		
		sqls = '"%s", "%s", "%s", "%s", "%s", %f, %d, %f, %f, %f, "%s", "%s"' % (date, 
		trade, name, ttype, order, price, number, postion, margin, profit, reason, comments)
		print sqls
		
		res = self.db.insert(self.table, sqls)
		return res
	
	def removeTrade (self, table):
		return
	
	def updateTrade (self, table):
		return
	
	def openTrade (self, trade, name, date, ttype, order, price, number, 
		reason=None, profit=0.0, comments=None, postion=0.0, margin=0.0):
		
		return self.__addTrade(trade, name, date, ttype, order, price, number, 
		reason, profit, comments, postion, margin)
		
	def openDTrade (self, trade, name, date, order, price, number, 
		reason=None, profit=0.0, comments=None, postion=0.0, margin=0.0):
		
		return self.openTrade(trade, name, date, 'D', order, price, number, 
		reason, profit, comments, postion, margin)
		
	def openKTrade (self, trade, name, date, order, price, number, 
		reason=None, profit=0.0, comments=None, postion=0.0, margin=0.0):
		
		return self.openTrade(trade, name, date, 'K', order, price, number, 
		reason, profit, comments, postion, margin)
	
				
	def tradeOver (self, trade, name, date, ttype, order, price, number, 
		reason=None, comments=None):
		
		if self.table is None:
			return
		
		cond = 'instr(Ord, "%s") and Trade = "%s" and Type = "%s"' % (order, trade, ttype)
		self.db.search(self.table, cond, "Price, Ord, Number")
		res = self.db.fetch(0)
		#print res
		#print res[0]
		
		if ttype == 'D':
			profit = price - res[0]
		elif ttype == 'K':
			profit = res[0] - price
		else:
			return
			
		profit = profit * number * 10
		#if res[2] >= number:
			#num = res[2] - number
		#else:
			#return
		
		oldord = res[1].strip(order)
		#print order
		#print profit
			
		res = self.__addTrade(trade, name, date, 'P', order, price, number, 
		reason, profit, comments)
		if res == 1:
			res = self.db.update(self.table, cond, 'Ord = "%s"' % oldord )
	
		return res
		
	def tradeHedge ():
		return 
	
