#! /usr/bin/python

'''
This module defines commonly used functions to do futures trading.
'''

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