#!/usr/bin/python
import sys
sys.path.append("..")
import db.mysqldb as sql

def test_mysql():
	def sqlDrop():
		import trade
		trd = trade.Trade('futures', 'trade_rec4')
		db = sql.MYSQL("localhost", "win", "winfwinf", 'futures') #should have exception here
		db.connect()
		db.drop('trade_rec4')
	sqlDrop()

if __name__=='__main__':
	test_mysql()
#	print "test finish\n"