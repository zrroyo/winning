#! /usr/bin/python

import os
import sys
sys.path.append("..")
import db.mysqldb as sql
import date

class Import:
	def __init__ (self, database='futures'):
		self.db = sql.MYSQL("localhost", 'win', 'winfwinf', database)
		self.db.connect()
		self.database = database
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
	def partReimport (self, tableFrom, tableTo, tFrom, tTo=None):
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
	def getRecordFieldSepBySpace (self, record, field=1):
		cmdStr = 'echo "%s" | awk \'{print $%d}\' ' % (record, field)
		res = os.popen(cmdStr.strip())
		#print res.read().strip()
		#print res
		return res.read().strip()
	
	# Get the value from the field specifed by $field from a $record in which 
	# each field is separated by comma.
	def getRecordFieldSepByComma (self, record, field=1):
		cmdStr = 'echo "%s" | awk \'BEGIN{FS=","}END{print $%d}\' ' % (record, field)
		res = os.popen(cmdStr.strip())
		#print res.read().strip()
		#print res
		return res.read().strip()
	
	# Return the max date in month.
	def _maxDateInMonth (self, month, Year):
		if month == 1:
			maxDate = '01-31'
		elif month == 2:
			maxDate = '02-29'
		elif month == 3:
			maxDate = '03-31'
		elif month == 4:
			maxDate = '04-30'
		elif month == 5:
			maxDate = '05-31'
		elif month == 6:
			maxDate = '06-30'
		elif month == 7:
			maxDate = '07-31'
		elif month == 8:
			maxDate = '08-31'
		elif month == 9:
			maxDate = '09-30'
		elif month == 10:
			maxDate = '10-31'
		elif month == 11:
			maxDate = '11-30'
		elif month == 12:
			maxDate = '12-31'
		else:
			return None
		
		date = '%s-' % Year
		date += maxDate
		return date
	
	# Decide the start date for a sub future determinded by year and 
	# month in a future table.
	def _startDateSubFuture (self, dateSet, year, month, endDays):
		if month > 12 or month < 1:
			return None
		
		maxDatePrevMonth = self._maxDateInMonth(month-1, year-1)
		
		#print maxDatePrevMonth
		if maxDatePrevMonth <= dateSet.firstDate():
			return dateSet.firstDate()
		
		return dateSet.getDateNextDays(maxDatePrevMonth, endDays+1)
		
	# Decide the end date for a sub future determinded by year and 
	# month in a future table.
	def _endDateSubFuture (self, dateSet, year, month, endDays):
		if month > 12 or month < 1:
			return None
		
		maxDatePrevMonth = self._maxDateInMonth(month-1, year)
		
		#print maxDatePrevMonth
		if maxDatePrevMonth >= dateSet.lastDate():
			return dateSet.lastDate()
		
		return dateSet.getDateNextDays(maxDatePrevMonth, endDays)
	
	# Make the future name with the future code, year and month.
	def _tableNameTemplate (self, futCode, year, month):
		if month > 12 or month < 1:
			return None
		
		year = year%2000
		if year < 10:
			year = '0%s' % year
			
		if month < 10:
			month = '0%s' % month
			
		name = '%s%s%s' % (futCode, year, month)
		#print name
		return name
	
	# Split a big future table which in consisted of many sub-future (future by year) tables 
	# into sub-futures tables.	
	def splitTableToSubFutures (self, futCode, dataTable, month, endDays, yearStart, yearEnd=0):
		if self.db.ifTableExist(dataTable) == False:
			print '\n	Table "%s" does not exist!\n' % dataTable
			return
		
		if month > 12 or month < 1:
			print '\n	Month "%s" is out of range [1~12]\n' % month
			return
		
		lcDateSet = date.Date(self.database, dataTable)
		year = yearStart
		
		while year >= yearEnd:
			startDate = self._startDateSubFuture(lcDateSet, year, month, endDays)
			endDate = self._endDateSubFuture(lcDateSet, year, month, endDays)
			tableName = self._tableNameTemplate(futCode, year, month)
			tableName += '_dayk'
			print tableName, startDate, endDate
			self.partReimport(dataTable, tableName, startDate, endDate)
			
			if startDate == lcDateSet.firstDate():
				break
			
			year -= 1
	
	def dropFutureTable (self, dataTable):
		return self.db.drop(dataTable)
	