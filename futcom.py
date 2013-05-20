#! /usr/bin/python

'''
This module defines commonly used functions to do futures trading.
'''

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
	