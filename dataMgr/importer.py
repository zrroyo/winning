#-*- coding:utf-8 -*-

'''
导入数据接口

将文华等行情软件下载的数据文件导入数据库。
'''

import os
import sys
sys.path.append("..")
import fileinput

from date import *
from db.mysqldb import *
from misc.debug import *
from misc.dateTime import *

class Import:
	
	#调试接口
	debug = Debug('Import', False)
	
	def __init__ (self, 
		database='futures'
		):
		self.db = MYSQL("localhost", 'win', 'winfwinf', database)
		self.db.connect()
		self.database = database
		return
	
	def __del__ (self):
		self.db.close()
	
	#准备导入，如果数据表不存在则使用模版导入
	def __prepareImport(self, 
		table,			#数据表名
		tableType='dayk',	#数据表类型
		):
		if self.db.ifTableExist(table):
			return True
		
		if tableType == 'dayk':
			template = 'templateDayk'
			
		self.db.createTableTemplate(table, template)
		
	#格式化时间
	def formatTime (self,
		time,	#待格式化的时间
		):
		return datetimeToStr(strToDatetime(time, '%m/%d/%Y'), '%Y-%m-%d')
	
	#将文件数据记录转换成字段列表
	def fileRecordToColumns (self,
		line,	#待转换的行（数据文件中的每一行）
		):
		time,open,highest,lowest,close,avg,sellVol,buyVol = line.rstrip('\r\n').split(',')
		return time,open,highest,lowest,close,avg,sellVol,buyVol
	
	#新导入一个数据表
	def newImport (self, 
		file,			#待导入的数据文件
		table,			#目标数据表
		timeFilters = None,	#过滤间期
		):
		self.__prepareImport(table)
		
		#如过滤间期有效则只导入指定区间的数据
		if timeFilters is not None:
			startTime,endTime = timeFilters.split(',')
		
		for line in fileinput.input(file):
			time,open,highest,lowest,close,avg,sellVol,buyVol = self.fileRecordToColumns(line)
			
			if timeFilters is not None:
				#忽略所有早于开始日期的数据
				if strToDatetime(time, '%m/%d/%Y') < strToDatetime(startTime, '%Y-%m-%d'):
					#self.debug.dbg('Ignore %s' % time)
					continue
				
				#已到截止日期，操作完成
				if strToDatetime(time, '%m/%d/%Y') > strToDatetime(endTime, '%Y-%m-%d'):
					#self.debug.dbg('Up to the end date %s' % endTime)
					fileinput.close()
					return
			
			#self.debug.dbg('New record: %s' % line.rstrip('\n'))
			time = self.formatTime(time)
			values = "'%s',%s,%s,%s,%s,%s,%s,%s,Null,Null" % (
						time,open,highest,lowest,close,avg,sellVol,buyVol)
			self.debug.dbg('Insert values %s' % values)
			self.db.insert(table, values)
	
	#从数据文件中追加数据
	def appendRecordsFromFile (self, 
		file,		#数据文件
		table,		#数据表
		endTime = None,	#截止时间
		):
		dateSet = Date(self.database, table)
		lastDate = dateSet.lastDate()
		
		for line in fileinput.input(file):
			time,open,highest,lowest,close,avg,sellVol,buyVol = self.fileRecordToColumns(line)
			
			#忽略所有大于endTime的数据，并结束
			if endTime is not None and strToDatetime(time, '%m/%d/%Y') > strToDatetime(endTime, '%Y-%m-%d'):
				self.debug.dbg('Appended all data until %s' % endTime)
				fileinput.close()
				return
			
			#略过所有已同步数据
			if strToDatetime(lastDate, '%Y-%m-%d') >= strToDatetime(time, '%m/%d/%Y'):
				continue
			
			time = self.formatTime(time)
			if self.db.ifRecordExist(table, 'Time', time):
				print "Found duplicate record: %s" % time
				#退出前关闭文件序列
				fileinput.close()
				break
			
			self.debug.dbg('Found new record: %s' % line.rstrip('\n'))
			
			values = "'%s',%s,%s,%s,%s,%s,%s,%s,Null,Null" % (
						time,open,highest,lowest,close,avg,sellVol,buyVol)
			self.debug.dbg('Insert values %s' % values)
			self.db.insert(table, values)
	
	#从目录下的数据文件中导入数据
	def appendRecordsFromDir (self, 
		directory,	#数据文件目录
		endTime = None,	#截止时间
		):
		pass
	
	# Reimport a part of records between date $Tfrom to date $tTo from 
	# tableFrom to new tableTo
	def partReimport (self, tableFrom, tableTo, tFrom, tTo=None):
		if self.db.ifTableExist(tableFrom) == False:
			return
		
		self.__prepareImport(tableTo)
		
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
		
		if month == 1:
			month = 12
			year -= 1
		else:
			month -= 1
		
		maxDatePrevMonth = self._maxDateInMonth(month, year-1)
		
		#print maxDatePrevMonth
		if maxDatePrevMonth <= dateSet.firstDate():
			return dateSet.firstDate()
		
		return dateSet.getDateNextDays(maxDatePrevMonth, endDays+1)
		
	# Decide the end date for a sub future determinded by year and 
	# month in a future table.
	def _endDateSubFuture (self, dateSet, year, month, endDays):
		if month > 12 or month < 1:
			return None
		
		if month == 1:
			month = 12
			year -= 1
		else:
			month -= 1
					
		maxDatePrevMonth = self._maxDateInMonth(month, year)
		
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
		
		lcDateSet = Date(self.database, dataTable)
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
	