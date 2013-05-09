#! /usr/bin/python

import sys
sys.path.append('..')
import strategy.turt1 as TURT
import dataMgr.data as data

database = 'history'
#time = '2013-5-7'
#days = 9

def printBound (table, time, days):
	dat = data.Data(database, table)
	print '\n%s lowest with %s days up to %s' % (table, days, time), dat.highestUpToDate(time, days)
	print '%s highest with %s days up to %s' % (table, days, time), dat.lowestUpToDate(time, days)


def showBound (time, days):
	printBound('m1309_dayk', time, days)
	printBound('sr1309_dayk', time, days)
	printBound('rb1310_dayk', time, days)
	printBound('pta1309_dayk', time, days)
	
	
if __name__ == '__main__':
	if len(sys.argv) != 3:
		print '2 arguments are required!'
		exit()
	#print 	len(sys.argv)
	time = sys.argv[1]
	days = int(sys.argv[2])
	showBound (time, days)

