#-*- coding:utf-8 -*-

'''
文华已不支持数据下载，需要支持从浏览数据中导入数据，故为hack版 :-)
'''

import os
import fileinput

from importer import *
from core.date import *
from misc.dateTime import *
from misc.debug import *

#h文华hack版数据导入接口
class WenhuaHackImporter(Import):
	
	#将文件数据记录转换成字段列表
	#override
	def fileRecordToColumns (self,
		line,	#待转换的行（数据文件中的每一行）
		):
		time,open,high,low,close,Volume,OpenInterest = line.rstrip('\r\n').split(',')
		avg = 0
		return time,open,high,low,close,avg,Volume,OpenInterest
	
	#格式化时间
	#override
	def formatTime (self,
		time,	#待格式化的时间
		):
		return datetimeToStr(strToDatetime(time, '%m/%d/%Y'), '%Y-%m-%d')
	
	#把数据文件转换为数据表名
	def recordsFileToTable (self,
		file,	#数据文件
		):
		file = file.rstrip('.txt').rstrip(' ')
		if file.find('PTA') >= 0:
			ret = file.replace('PTA1', 'TA')
		elif file.find('白糖') >= 0:
			ret = file.replace('白糖1', 'SR')
		elif file.find('玻璃') >= 0:
			ret = file.replace('玻璃1', 'FG')
		elif file.find('菜粕') >= 0:
			ret = file.replace('菜粕1', 'RM')
		elif file.find('豆粕') >= 0:
			ret = file.replace('豆粕', 'm')
		elif file.find('鸡蛋') >= 0:
			ret = file.replace('鸡蛋', 'jd')
		elif file.find('螺纹') >= 0:
			ret = file.replace('螺纹', 'rb')
		elif file.find('棕榈') >= 0:
			ret = file.replace('棕榈', 'p')
		else:
			return None
			
		ret += '_dayk'
		return ret
		