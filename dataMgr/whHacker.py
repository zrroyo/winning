#-*- coding:utf-8 -*-

'''
文华已不支持数据下载，需要支持从浏览数据中导入数据，故为hack版 :-)
'''

import os
import fileinput

from importer import *
from date import *
from misc.dateTime import *
from misc.debug import *

#h文华hack版数据导入接口
class WenhuaHackImporter(Import):
	
	#调试接口
	debug = Debug('WenhuaHackImporter', True)
	
	#从数据文件中追加数据
	def appendRecordsFromFile (self, 
		file,	#数据文件
		table,	#数据表
		):
		dateSet = Date(self.database, table)
		lastDate = dateSet.lastDate()
		
		for line in fileinput.input(file):
			time,open,highest,lowest,close,sellVol,buyVol = line.rstrip('\r\n').split(',')
			if strToDatetime(lastDate, '%Y-%m-%d') >= strToDatetime(time, '%m/%d/%Y'):
				continue
			
			self.debug.dbg('Found new record: %s' % line.rstrip('\n'))
			
			time = datetimeToStr(strToDatetime(time, '%m/%d/%Y'), '%Y-%m-%d')
			values = "'%s',%s,%s,%s,%s,0,%s,%s,Null,Null" % (time,open,highest,lowest,close,sellVol,buyVol)
			self.debug.dbg('Insert values %s' % values)
			self.db.insert(table, values)
	
	#把数据文件转换为数据表名
	def __fileToTableName (self,
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
	
	#从目录下的数据文件中导入数据
	def appendRecordsFromDir (self, 
		diretory,	#数据文件目录
		):
		files = os.listdir(diretory)
		for f in files:
			table = self.__fileToTableName(f)
			file = diretory.rstrip('/') + '/' + f
			self.debug.dbg(file)
			self.appendRecordsFromFile(file, table)
	
