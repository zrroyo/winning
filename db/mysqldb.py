#! /usr/bin/python
# coding=gbk

'''
Core MySQL Interface

This class defines a basic framework to access MySQL database, which makes 
access database much easilier. 
'''

import sys
import types
import MySQLdb as sql
import db
import exc

class MYSQL(db.DB):
	# Initialize the connection to MySQL database.
	def connect (self):
		self.conn = sql.connect(self.host, self.user, self.passwd, self.db)
		self.cursor = self.conn.cursor()
		return True
			
	# Set @table as default table.
	def setDefTable (self, table):
		self.table = table
		return True
			
	# Execute SQL sentence.
	def execSql (self, sqls):
		if self.cursor == None:
			return None
		try:
			res = self.cursor.execute(sqls)
			return res
		except :
			exc.logExcSql()
	
	# Fetch all searched results, and it is only used following execSql() if needed.
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
	
	# Do a simple search. Search condition and returned fields must be pointed out 
	# by @cond and @field.
	def search (self, table, cond, field="*"):
		if self.cursor == None:
			return None
	
		if cond == None:
			sqls = "select %s from %s" % (field, table)
		else:
			sqls = "select %s from %s where %s " % (field, table, cond)
		
		res = self.execSql(sqls)
		return res
	
	# Insert a new record filled by @values into @table 
	def insert (self, table, values):
		if self.cursor == None:
			return None
		
		sqls = "insert into %s values ( %s )" % (table, values)
		res = self.execSql(sqls)
		return res
	
	# Update a record matching @cond using @values to @table.
	def update (self, table, cond, values):
		if self.cursor == None:
			return None
				
		sqls = "update %s set %s where %s" % (table, values, cond)
		res = self.execSql(sqls)
		return res
			
	# Remove a record matching @cond from @table.
	def remove (self, table, cond):
		if self.cursor == None:
			return None
		
		sqls = "delete from %s where %s" % (table, cond)
		res = self.execSql(sqls)
		return res
	
	# Close a connection to database.
	def close (self):
		self.cursor.close()
		self.conn.close()
		return
		
	# Drop a table from database.
	def drop (self, table):
		sqls = 'drop table %s' % table
		res = self.execSql(sqls)
		return res
	
	# Set the primary keys for a table.
	def attrSetPrimary (self, table, field):
		sqls = 'alter table %s add primary key(%s)' % (table, field)
		res = self.execSql(sqls)
		return res
	
	#def attrSetNotNull (self, table, field):
		#return
		
	# Return if a table existed in database.
	def ifTableExist (self, table):
		sqls = 'show tables like \'%s\'' % (table)
		res = self.execSql(sqls)
		if res == 1:
			return True
		else:
			return False
		
	# Create a data table using template.
	def createTableTemplate (self, table, template):
		if self.ifTableExist(table):
			return
			
		sqls = 'create table %s like %s' % (table, template)
		res = self.execSql(sqls)
		return res
	
	# Return if a record already exists in a data table.
	def ifRecordExist (self, table, primaryKey, value):
		sqls = 'select * from %s where %s = "%s"' % (table, primaryKey, value)
		res = self.execSql(sqls)
		
		if res == 1:
			return True
		else:
			return False
		