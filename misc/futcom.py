#! /usr/bin/python
#-*- coding:utf-8 -*-

'''
This module defines commonly used functions to do futures trading.
'''

import time
import db.mysqldb as sql

# Transfer a futCode to a data table.
def futcodeToDataTable (futCode):
	if futCode.find('_dayk') != -1:
		return futCode
	else:
		return '%s_dayk' % futCode

# Transfer a set of futCodes to a set of data tables.
def futcodeSetToDataTables (futcodeSet):
	newSet = []
	for futCode in futcodeSet:
		newSet.append(futcodeToDataTable(futCode))
		
	return newSet
	
# Return if a table marked by futCode does exist.	
def futureTalbeExists (futCode, database):
	db = sql.MYSQL("localhost", 'win', 'winfwinf', database)
	db.connect()
	
	ret = db.ifTableExist(futCode)
	
	db.close()
	
	return ret
	
#生成临时名称后缀
def tempNameSuffix():
	tempFileName = time.strftime('%Y%m%d%H%M%S')
	return tempFileName

#将todoList列表的内容按filter参数的指定规则进行过滤。
def filtering (todoList, filter):
	'''
	支持'*'和'!'两种过滤方式。
	‘*’表示任意多个字符，'!'表示不包含。
	'''
	filter1 = filter.split('!')[0]
	filters = filter1.split('*')
		
	for f in filters:
		if f is not None:
			todoList = [test for test in todoList if test.find(f) != -1]
			
	if filter[0] != '*':
		todoList = [test for test in todoList if test[0] == filter[0]]
		
	revert = filter.split('!')[1:]
	if len(revert) == 0:
		return todoList
		
	for f in revert:
		if f != '':
			todoList = [test for test in todoList if test.find(f) == -1]
		
	#print todoList
	return todoList
	