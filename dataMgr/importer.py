#! /usr/bin/python

import os
import db.mysqldb as sql

class Import:
	def __init__ (self, database='futures'):
		self.db = sql.MYSQL("localhost", 'win', 'winfwinf', database)
		self.db.connect()
		return
	
	def __exit__ (self):
		self.db.close()
		return
	
	# Prepare to import records from $dataFile to $dataTable.
	# If dataTable does not exist, create it using template.
	def prepareImport(self, table, tableType='dayk'):
		if self.db.ifTableExist(table):
			return True
		
		if tableType == 'dayk':
			template = 'templateDayk'
			
		self.db.createTableTemplate(table, template)
		
	# Newly import data records from $dataFile to $dataTable
	def newImport (self, dataFile, dataTable):
		return
	
	# Reimport a part of records between date $Tfrom to date $tTo from 
	# tableFrom to new tableTo
	def partReimport(self, tableFrom, tableTo, tFrom, tTo=None):
		if self.db.ifTableExist(tableFrom) == False:
			return
		
		self.prepareImport(tableTo)
		
		if (tTo is None):
			sqls = 'insert %s (select * from %s where Time >= \'%s\' order by Time asc)' % (tableTo, tableFrom, tFrom)
		else:
			sqls = 'insert %s (select * from %s where Time >= \'%s\' and Time <= \'%s\' order by Time asc)' % (tableTo, tableFrom, tFrom, tTo)
		res = self.db.execSql(sqls)
		
		#print 'partReimportTo'
		return res
		
	# Get the value from the field specifed by $field from a $record in which 
	# each field is separated by space.
	def getRecordFieldSepBySpace(self, record, field=1):
		cmdStr = 'echo "%s" | awk \'{print $%d}\' ' % (record, field)
		res = os.popen(cmdStr.strip())
		#print res.read().strip()
		#print res
		return res.read().strip()
	
	# Get the value from the field specifed by $field from a $record in which 
	# each field is separated by comma.
	def getRecordFieldSepByComma(self, record, field=1):
		cmdStr = 'echo "%s" | awk \'BEGIN{FS=","}END{print $%d}\' ' % (record, field)
		res = os.popen(cmdStr.strip())
		#print res.read().strip()
		#print res
		return res.read().strip()
	
