#-*- coding:utf-8 -*-

import sys
sys.path.append("..")

from db.mysqldb import *

#海龟数据类
class TurtData:
	def __init__ (self, 
		database, 
		table,
		):
		self.db = MYSQL("localhost", 'win', 'winfwinf', database)
		self.table = table
		self.db.connect()
		
	def __exit__ (self):
		self.db.close()
		
	def updateTr (self, 
		time, 
		ltr,
		):
		cond = 'Time=\'%s\'' % (time)
		value = 'Tr=%s' % (ltr)
		#print cond, value
		self.db.update(self.table, cond, value)
	
	def updateAtr (self, 
		time, 
		atr,
		):
		cond = 'Time=\'%s\'' %(time)
		value = 'Atr=%s' % (atr)
		#print cond, value
		self.db.update(self.table, cond, value)
		
	# Check whether 'Atr' field in data table are all calculated.
	def checkAtr (self):
		cond = 'Atr is NULL'
		
		res = self.db.search (self.table, cond)
		if res > 0:
			return False
		else:
			return True
		
	# Get the 'Atr' filed for a record specified by @time
	def getAtr (self, 
		time,
		):
		cond = 'Time=\'%s\'' % (time)
		
		self.db.search (self.table, cond, 'Atr')
		res = self.db.fetch(0)
		#print res

		return res[0]
	