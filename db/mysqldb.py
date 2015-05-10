#-*- coding:utf-8 -*-

'''
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>

MySQL数据库访问接口
'''

import sys
sys.path.append('..')

import types
import MySQLdb as sql
import exc
from db import *
from misc.debug import *

#MySQL数据库接口
class MYSQL(DB):
	
	debug = Debug('MYSQL', False)	#调试接口
	
	#连接数据库
	def connect (self,
		database = None,	#将要连接的数据库
		):
		if database is not None:
			db = database
		elif self.db is not None:
			db = self.db
		else:
			self.debug.error("Found database is None, invalid!")
			return
		
		self.conn = sql.connect(self.host, self.user, self.passwd, db)
		self.cursor = self.conn.cursor()
		return True
	
	#设置默认数据表
	def setDefTable (self, 
		table,	#数据表
		):
		self.table = table
		return True
	
	#执行SQL语句
	def execSql (self, 
		sqls,	#SQL语句
		):
		self.debug.dbg(sqls)
		
		if self.cursor == None:
			return None
		try:
			res = self.cursor.execute(sqls)
			return res
		except :
			exc.logExcSql()
	
	#取出查询结果，通常紧跟在execSql()之后
	def fetch (self, 
		line = 0,	#默认取出第一行
		):
		if self.cursor == None:
			return None
	
		res = self.cursor.fetchall()
			
		if line == 'all':
			return res
		elif type(line) is types.IntType:
			return res[line]
		else:
			return None
	
	#查询（搜索）数据库
	def search (self, 
		table,		#数据表
		cond = None, 	#查询条件
		field = "*",	#所要查询的字段
		):
		if self.cursor == None:
			return None
	
		if cond == None:
			sqls = "select %s from %s" % (field, table)
		else:
			sqls = "select %s from %s where %s " % (field, table, cond)
		
		res = self.execSql(sqls)
		return res
	
	#插入记录
	def insert (self,
		table,	#数据表
		values,	#记录值
		):
		if self.cursor == None:
			return None
		
		sqls = "insert into %s values ( %s )" % (table, values)
		res = self.execSql(sqls)
		return res
	
	#更新记录
	def update (self,
		table,	#数据表
		cond, 	#查询条件
		values,	#记录值
		):
		if self.cursor == None:
			return None
		
		sqls = "update %s set %s where %s" % (table, values, cond)
		res = self.execSql(sqls)
		return res
	
	#移除记录
	def remove (self, 
		table,	#数据表
		cond, 	#查询条件
		):
		if self.cursor == None:
			return None
		
		sqls = "delete from %s where %s" % (table, cond)
		res = self.execSql(sqls)
		return res
	
	#关闭数据连接
	def close (self):
		self.cursor.close()
		self.conn.close()
		
	#删除数据表
	def drop (self, 
		table,	#数据表
		):
		sqls = 'drop table %s' % table
		res = self.execSql(sqls)
		return res
	
	#设置数据表主键
	def attrSetPrimary (self, 
		table,	#数据表
		field,	#主键字段
		):
		sqls = 'alter table %s add primary key(%s)' % (table, field)
		res = self.execSql(sqls)
		return res
	
	#def attrSetNotNull (self, table, field):
		#return
		
	#返回是否数据表已存在
	def ifTableExist (self, 
		table,	#数据表
		):
		sqls = 'show tables like \'%s\'' % (table)
		res = self.execSql(sqls)
		if res == 1:
			return True
		else:
			return False
		
	#用数据表模版创建新表
	def createTableTemplate (self, 
		table, 		#数据表
		template,	#表模版
		):
		if self.ifTableExist(table):
			return
			
		sqls = 'create table %s like %s' % (table, template)
		res = self.execSql(sqls)
		return res
	
	#返回数据记录是否存在
	def ifRecordExist (self, 
		table, 		#数据表
		primaryKey, 	#主键
		value,		#主键值
		):
		sqls = 'select * from %s where %s = "%s"' % (table, primaryKey, value)
		res = self.execSql(sqls)
		
		if res == 1:
			return True
		else:
			return False
		