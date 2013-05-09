#! /usr/bin/python

'''
This is the core framework to run regression tests.
'''

import sys
from optparse import OptionParser
import string
import db.mysqldb as sql

# List all possible regression tests in database.
def listFutureTables (database):
	regSet = possibleRegressionTests(database)
	print "\nAll possible regression test tables in '%s:'\n" % database
	for test in regSet:
		print test

# Get all possible regression tests in database.
def possibleRegressionTests (database):
	db = sql.MYSQL("localhost", 'win', 'winfwinf', database)
	db.connect()
	
	sqls = 'show tables'
	db.execSql(sqls)
	
	res = list(db.fetch('all'))
	
	regSet = []
	for test in res:
		regSet.append(test[0])
		
	# Filter all tables not ended by '_dayk'
	regSet = [test for test in regSet if test.find('_dayk') != -1]	
		
	#print regSet
	
	db.close()
	return regSet

# Regression Filter omits all tests which do not match @futcode in @regSet.
def regressionFilter (regSet, futcode):
	retRegSet = [test for test in regSet if test.find(futcode) != -1]
	return retRegSet

# Core function to do regression for @test with @strategy
def doRegression (database, test, strategy):
	tradeRec = 'dummy'	# Currently, does not support Trade Recording.
	minPosIntv=40
	priceUnit=10
	
	if strategy == 'turtle':
		import strategy.turtle as turtle
		strategy = turtle.Turtle(test, test, tradeRec, database)
		strategy.setAttrs(3, 1, minPosIntv, priceUnit)
	elif strategy == 'turt1':
		import strategy.turt1 as turt1	
		strategy = turt1.Turt1(test, test, tradeRec, database)
		strategy.setAttrs(3, 1, minPosIntv, priceUnit)
	else:
		print "\nUnknown strategy '%s'.\n" % options.strategy
		return
	
	strategy.run()

# Regression subsystem option handler transfering options to actions.
def regressionOptionsHandler (options, args):
	if options.database is None:
		print "\nPlease specify database using '-b'.\n"
		return
	
	database = options.database
	
	if options.list:
		listFutureTables (database)
		return

	if options.strategy is None:
		print "\nPlease specify a strategy to do regression using '-s'.\n"
		return	
	
	regSet = []
	if options.muster:
		regSet = options.muster.split(',')
	elif options.all:
		regSet = possibleRegressionTests(database)
	else:
		regSet = possibleRegressionTests(database)
		
	if options.futcode:
		regSet = regressionFilter(regSet, options.futcode)
		
	#print regSet
	for test in regSet:
		doRegression(database, test, options.strategy)
	
# Regression subsystem Option Parser. Called in win.py.
def regressionOptionsParser (parser):
	parser.add_option('-a', '--all', action="store_true", dest='all', 
			help='Run all posssible regression tests.')
	parser.add_option('-l', '--list', action="store_true", dest='list', 
			help='List all posssible regression tests.')
	parser.add_option('-m', '--muster', dest='muster', 
			help='Only do regression tests for the Futures listed in this set.')
	parser.add_option('-s', '--strategy', dest='strategy', 
			help='The strategy used to do regression tests.')
	parser.add_option('-f', '--futcode', dest='futcode', 
			help='Only do regression tests for the Futures matching this future code.')
	parser.add_option('-b', '--database', dest='database', 
			help='The database with which regreesion tests will be done.')
			
	(options, args) = parser.parse_args()

	regressionOptionsHandler(options, args)
