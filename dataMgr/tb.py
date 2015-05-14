#-*- coding:utf-8 -*-

'''
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2015年 05月 09日 星期六 23:39:48 CST

TB版数据导入数据库
'''

from importer import *
from date import *
from misc.dateTime import *
from misc.debug import *

#TB版数据导入接口
class TBImporter(Import):
	
	#调试接口
	debug = Debug('TBImporter', False)
	
	#将文件数据记录转换成字段列表
	#OVERRIDE
	def fileRecordToColumns (self,
		line,	#待转换的行（数据文件中的每一行）
		):
		time,open,high,low,close,Volume,OpenInterest = line.rstrip('\r\n').split(',')
		avg = 0
		return time,open,high,low,close,avg,Volume,OpenInterest
	
	#时间格式字符串
	#OVERRIDE
	def strTimeFormat (self):
		return '%Y/%m/%d %H:%M'
	
	#格式化时间
	#OVERRIDE
	def formatTime (self,
		time,	#待格式化的时间
		):
		#TB数据中的时间已经为数据库支持格式，不用再转化
		return time
	
	#新导入一个数据表
	#OVERRIDE
	def newImport (self, 
		file,				#待导入的数据文件
		table,				#目标数据表
		timeFilters = None,		#过滤间期
		template = 'templateMink',	#数据表类型（模版）,修改默认不同于父类
		):
		return Import.newImport(self, file, table, timeFilters, template)
	