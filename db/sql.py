#! /usr/bin/env python
#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2015年 05月 08日 星期五 23:35:11 CST

数据库访问的通用接口，简化数据库的连接。
"""

from mysqldb import MYSQL

#数据库通用接口
class SQL(MYSQL):
	host 	= '127.0.0.1'
	user	= 'win'
	passwd	= 'winfwinf'

	def __init__ (self):
		MYSQL.__init__(self, self.host, self.user, self.passwd)
#测试
def doTest ():
	db = SQL()
	db.connect('history')
	
	#db = MYSQL("localhost", 'win', 'winfwinf', 'history')
	#db.connect()
	
	strSql = 'select * from p1409_dayk limit 1'
	#db.search('p1409_dayk', )
	db.execSql(strSql)
	print db.fetch(5)

	db.connect('history2')
	strSql = "insert templateMink values ('2010/04/07 13:49',6970,6972,6970,6972,0,562,241906,Null,Null)"
	db.execSql(strSql)
	
if __name__ == '__main__':
	doTest()
	