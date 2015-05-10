#! /usr/bin/python
#-*- coding:utf-8 -*-

'''
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2015年 05月 08日 星期五 23:35:11 CST

This program is provided under the Gnu General Public License (GPL)
version 2 ONLY.
'''

'''
数据库访问的通用接口，简化数据库的连接。
'''

from mysqldb import *

#数据库通用接口
class SQL(MYSQL):
	host 	= 'localhost'
	user	= 'win'
	passwd	= 'winfwinf'
	
	def __init__ (self):
		#不做具体操作，只是为了不再调用父类的初始化接口
		pass

##测试
#def doTest ():
	#db = SQL()
	#db.connect('history')
	
	##db = MYSQL("localhost", 'win', 'winfwinf', 'history')
	##db.connect()
	
	#strSql = 'select * from p1409_dayk limit 1'
	##db.search('p1409_dayk', )
	#db.execSql(strSql)
	#print db.fetch(0)
	
	#db.connect('history2')
	#strSql = "insert templateMink values ('2010/04/07 13:49',6970,6972,6970,6972,0,562,241906,Null,Null)"
	#db.execSql(strSql)
	
#if __name__ == '__main__':
	#doTest()
	