#-*- coding:utf-8 -*-

'''
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>

导入数据接口

将文华等行情软件下载的数据文件导入数据库。
'''

import os
import sys
sys.path.append("..")
import fileinput

from date import *
from db.sql import *
from misc.debug import *
from misc.dateTime import *

class Import:
	def __init__ (self, 
		database = 'futures',	#默认连接数据库
		debug = False,		#是否调试
		):
		self.db = SQL()
		self.db.connect(database)
		self.database = database
		self.debug = Debug('Import', debug)	#调试接口
	
	def __del__ (self):
		self.db.close()
	
	#准备导入，如果数据表不存在则使用模版导入
	def __prepareImport(self, 
		table,				#数据表名
		template = 'templateDayk',	#数据表类型（模版）
		):
		if self.db.ifTableExist(table):
			return True
		
		self.db.createTableTemplate(table, template)
	
	#格式化时间
	#MUST_OVERRIDE
	def formatTime (self,
		time,	#待格式化的时间
		):
		return datetimeToStr(strToDatetime(time, self.strTimeFormat()), self.strTimeFormat())
	
	#时间格式字符串
	#MUST_OVERRIDE
	def strTimeFormat (self):
		#必须指定为数据文件中的时间格式，如不同于如下
		#格式需要在子类中重载，重要！
		return '%m/%d/%Y'
	
	#将文件数据记录转换成字段列表
	#MUST_OVERRIDE
	def fileRecordToColumns (self,
		line,	#待转换的行（数据文件中的每一行）
		):
		time,open,high,low,close,avg,Volume,OpenInterest = line.rstrip('\r\n').split(',')
		return time,open,high,low,close,avg,Volume,OpenInterest
	
	#新导入一个数据表
	def newImport (self, 
		file,				#待导入的数据文件
		table,				#目标数据表
		timeFilters = None,		#过滤间期
		template = 'templateDayk',	#数据表类型（模版）
		):
		self.__prepareImport(table, template)
		
		#如过滤间期有效则只导入指定区间的数据
		if timeFilters:
			tf = timeFilters.split(',')
			startTime = tf[0]
			endTime = None
			if len(tf) == 2:
				endTime = tf[1]
		
		for line in fileinput.input(file):
			time,open,high,low,close,avg,Volume,OpenInterest = self.fileRecordToColumns(line)
			
			if timeFilters:
				timeRecord = strToDatetime(time, self.strTimeFormat())
				#忽略所有早于开始日期的数据
				if startTime and timeRecord < strToDatetime(startTime, self.strTimeFormat()):
					#self.debug.dbg('Ignore %s' % time)
					continue
				
				#已到截止日期，操作完成
				if endTime and timeRecord > strToDatetime(endTime, self.strTimeFormat()):
					#self.debug.dbg('Up to the end date %s' % endTime)
					fileinput.close()
					return
			
			#self.debug.dbg('New record: %s' % line.rstrip('\n'))
			time = self.formatTime(time)
			values = "'%s',%s,%s,%s,%s,%s,%s,%s,Null,Null" % (
						time,open,high,low,close,avg,Volume,OpenInterest)
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
			time,open,high,low,close,avg,Volume,OpenInterest = self.fileRecordToColumns(line)
			
			#忽略所有大于endTime的数据，并结束
			if endTime and strToDatetime(time, self.strTimeFormat()) > strToDatetime(endTime, self.strTimeFormat()):
				self.debug.dbg('Appended all data until %s' % endTime)
				fileinput.close()
				return
			
			#略过所有已同步数据
			if strToDatetime(lastDate, '%Y-%m-%d') >= strToDatetime(time, self.strTimeFormat()):
				continue
			
			time = self.formatTime(time)
			if self.db.ifRecordExist(table, 'Time', time):
				self.debug.dbg("Found duplicate record: %s" % time)
				#退出前关闭文件序列
				fileinput.close()
				break
			
			self.debug.dbg('Found new record: %s' % line.rstrip('\n'))
			
			values = "'%s',%s,%s,%s,%s,%s,%s,%s,Null,Null" % (
						time,open,high,low,close,avg,Volume,OpenInterest)
			self.debug.dbg('Insert values %s' % values)
			self.db.insert(table, values)
			
		print "%s is OK" % table
	
	#把数据文件转换为数据表名
	#MUST_OVERRIDE
	def recordsFileToTable (self,
		file,	#数据文件
		):
		#如果不同于以下格式，则必须重载此函数
		return '%s_dayk' % file
	
	#从目录下的数据文件中导入数据
	def appendRecordsFromDir (self, 
		directory,	#数据文件目录
		endTime = None,	#截止时间
		):
		files = os.listdir(directory)
		for f in files:
			table = self.recordsFileToTable(f)
			file = directory.rstrip('/') + '/' + f
			self.debug.dbg(file)
			self.appendRecordsFromFile(file, table, endTime)
	
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
	
	#删掉数据表
	def dropDataTable (self, table):
		return self.db.drop(table)
	