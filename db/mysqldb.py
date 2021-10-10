#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>

MySQL数据库访问接口
"""

import sys
sys.path.append('..')

import MySQLdb as sql
from db import DB
from misc.debug import Debug

# MySQL数据库接口
class MYSQL(DB):
	def __init__ (self,
		host,
		user,
		passwd,
		db = None,
		):
		DB.__init__(self, host, user, passwd, db)
		self.debug = Debug('MYSQL', False)	#调试接口
		self.conn = None
		self.cursor = None
		self.table = None

	# 连接数据库
	def connect (self,
		database = None,	#将要连接的数据库
		):
		if database:
			self.db = database

		self.conn = sql.connect(self.host, self.user, self.passwd, self.db)
		self.conn.autocommit(1)
		self.conn.ping(True)
		self.cursor = self.conn.cursor()
		return True
	
	# 设置默认数据表
	def setDefTable (self, 
		table,	#数据表
		):
		self.table = table

	# 执行SQL语句
	def execSql (self,
		strSql,	#SQL语句
		):
		try:
			self.debug.dbg(strSql)
			res = self.cursor.execute(strSql)
			return res
		except AttributeError, e:
			self.debug.error("execSql: %s" % e)
			return None
	
	# 取出查询结果，通常紧跟在execSql()之后
	def fetch (self, 
		line = 0,	#默认取出第一行
		):
		try:
			res = self.cursor.fetchall()
			if line == 'all':
				return res
			return res[line]

		except (AttributeError, TypeError), e:
			self.debug.error("fetch: %s" % e)
			return None
		except IndexError, e:
			self.debug.error("fetch: found wrong index, error: %s" % e)
			return None
	
	# 查询数据库
	def search (self, 
		table,		#数据表
		cond = None, 	#查询条件
		field = "*",	#所要查询的字段
		):
		if not cond:
			strSql = "select %s from %s" % (field, table)
		else:
			strSql = "select %s from %s where %s " % (field, table, cond)

		res = self.execSql(strSql)
		return res

	# 插入记录
	def insert (self,
		table,	#数据表
		values,	#记录值
		):
		strSql = "insert into %s values ( %s )" % (table, values)
		res = self.execSql(strSql)
		return res
	
	# 更新记录
	def update (self,
		table,	#数据表
		cond, 	#查询条件
		values,	#记录值
		):
		strSql = "update %s set %s where %s" % (table, values, cond)
		res = self.execSql(strSql)
		return res
	
	# 移除记录
	def remove (self, 
		table,	#数据表
		cond, 	#查询条件
		):
		strSql = "delete from %s where %s" % (table, cond)
		res = self.execSql(strSql)
		return res
	
	# 关闭数据连接
	def close (self):
		self.cursor.close()
		self.conn.close()
		
	# 删除数据表
	def drop (self, 
		table,	#数据表
		):
		strSql = 'drop table %s' % table
		res = self.execSql(strSql)
		return res
	
	# 设置数据表主键
	def attrSetPrimary (self, 
		table,	#数据表
		field,	#主键字段
		):
		strSql = 'alter table %s add primary key(%s)' % (table, field)
		res = self.execSql(strSql)
		return res
	
	# 返回是否数据表已存在
	def ifTableExist (self, 
		table,	#数据表
		):
		strSql = 'show tables like \'%s\'' % (table)
		res = self.execSql(strSql)
		if res == 1:
			return True
		else:
			return False
		
	# 用数据表模版创建新表
	def createTableTemplate (self, 
		table, 		#数据表
		template,	#表模版
		):
		if self.ifTableExist(table):
			return
			
		strSql = 'create table %s like %s' % (table, template)
		res = self.execSql(strSql)
		return res
	
	# 返回数据记录是否存在
	def ifRecordExist (self, 
		table, 		#数据表
		primaryKey, 	#主键
		value,		#主键值
		):
		strSql = 'select * from %s where %s = "%s"' % (table, primaryKey, value)
		res = self.execSql(strSql)

		if res == 1:
			return True
		else:
			return False
