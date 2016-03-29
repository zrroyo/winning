#!/usr/bin/env python

class DB:
	def __init__ (self, host, user, passwd, db):
		self.host = host
		self.user = user
		self.passwd = passwd
		self.db = db
	
	def __del__ (self):
		pass
	
	def connect (self, database):
		pass
	
	def execSql (self, strSql):
		pass
	
	def fetch (self, line):
		pass
		
	def search (self, table, cond, field):
		pass
	
	def insert (self, table, values):
		pass
	
	def update (self, table, cond, values):
		pass
	
	def remove (self, table, cond):
		pass
	
	def close (self):
		pass
	
	def drop (self, table):
		pass
	
	def createTable (self):
		pass
	
	def attrSetPrimary (self, table, field):
		pass
	
	def attrSetNotNull (self):
		pass
	