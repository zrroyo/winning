#! /usr/bin/python

import sys
sys.path.append('..')
import strategy.turt1 as TURT
import dataMgr.data as data

database = 'history'
#time = '2013-5-7'
#days = 9

def printBound (table, time, days, field):
	dat = data.Data(database, table)
	print '\n%s highest with %s days up to %s' % (table, days, time), dat.highestUpToDate(time, days, field)
	print '%s lowest with %s days up to %s' % (table, days, time), dat.lowestUpToDate(time, days, field)


def showBound (time, days, field):
	printBound('m1309_dayk', time, days, field)
	printBound('sr1309_dayk', time, days, field)
	printBound('rb1310_dayk', time, days, field)
	printBound('pta1309_dayk', time, days, field)
	
	
if __name__ == '__main__':
	if len(sys.argv) < 3:
		print '2 arguments are required!'
		exit()
	#print 	len(sys.argv)
	
	field = 'Close'
	time = sys.argv[1]
	days = int(sys.argv[2])
	if len(sys.argv) == 4:
		field = sys.argv[3]
	
	showBound (time, days, field)

