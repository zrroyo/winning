#! /usr/bin/python
# coding=gbk

import sys
import types
import MySQLdb as sql
import db
import exc

class MYSQL(db.DB):
	def connect (self):
		self.conn = sql.connect(self.host, self.user, self.passwd, self.db)
		self.cursor = self.conn.cursor()
		return True
			
	def setDefTable (self, table):
		self.table = table
		return True
			
	def execSql (self, sqls):
		if self.cursor == None:
			return None
		try:
			res = self.cursor.execute(sqls)
			return res
		except :
			exc.logExcSql()
	
	def fetch (self, line=0):
		if self.cursor == None:
			return None
			
		res = self.cursor.fetchall()
			
		if line == 'all':
			return res
		elif type(line) is types.IntType:
			return res[line]
		else:
			return None
	
	def search (self, table, cond, field="*"):
		if self.cursor == None:
			return None
	
		if cond == None:
			sqls = "select %s from %s" % (field, table)
		else:
			sqls = "select %s from %s where %s " % (field, table, cond)
		
		res = self.execSql(sqls)
		return res
	
	def insert (self, table, values):
		if self.cursor == None:
			return None
		
		sqls = "insert into %s values ( %s )" % (table, values)
		res = self.execSql(sqls)
		return res
	
	def update (self, table, cond, values):
		if self.cursor == None:
			return None
				
		sqls = "update %s set %s where %s" % (table, values, cond)
		res = self.execSql(sqls)
		return res
			
	def remove (self, table, cond):
		if self.cursor == None:
			return None
		
		sqls = "delete from %s where %s" % (table, cond)
		res = self.execSql(sqls)
		return res
	
	def close (self):
		self.cursor.close()
		self.conn.close()
		return
		
	def drop (self, table):
		sqls = 'drop table %s' % table
		res = self.execSql(sqls)
		return res
	
	def attrSetPrimary (self, table, field):
		sqls = 'alter table %s add primary key(%s)' % (table, field)
		res = self.execSql(sqls)
		return res
	
	#def attrSetNotNull (self, table, field):
		#return
		
	def ifTableExist (self, table):
		sqls = 'show tables like \'%s\'' % (table)
		res = self.execSql(sqls)
		if res == 1:
			return True
		else:
			return False
		
	def createTableTemplate (self, table, template):
		if self.ifTableExist(table):
			return
			
		sqls = 'create table %s like %s' % (table, template)
		res = self.execSql(sqls)
		return res
	