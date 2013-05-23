#! /usr/bin/python

'''
This is the core framework to run regression tests.
'''

import sys
from optparse import OptionParser
import string
import db.mysqldb as sql
import futcom

# Regression Filter omits all tests which do not match @filter in @regSet.
def regressionFilter (regSet, filter):
	filters = filter.split('*')
	
	for f in filters:
		if f is not None:
			regSet = [test for test in regSet if test.find(f) != -1]
	return regSet
	
# List all possible regression tests in database.
def listFutureTables (database, filter):
	regSet = possibleRegressionTests(database)
	if filter is not None:
		regSet = regressionFilter(regSet, filter)
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

# Core function to do regression for @test with @strategy.
def doRegression (options, database, test, strategy):
	tradeRec = 'dummy'	# Currently, does not support Trade Recording.
	maxPos = 3
	minPos = 1
	minPosIntv=40
	priceUnit=10
	
	if strategy == 'turtle':
		import strategy.turtle as turtle
		strategy = turtle.Turtle(test, test, tradeRec, database)
		strategy.setAttrs(maxPos, minPos, minPosIntv, priceUnit)
	elif strategy == 'turt1':
		if options.extra:
			args = options.extra.split(',')
			if len(args) == 4:
				maxPos = int(args[0])
				minPos = int(args[1])
				minPosIntv= int(args[2])
				priceUnit= int(args[3])
				print args
			else:
				print "\nExtra imformation contains incomplete or wrong attributes for Turt strategy.\n"
				exit()
			
		import strategy.turt1 as turt1	
		strategy = turt1.Turt1(test, test, tradeRec, database)
		strategy.setAttrs(maxPos, minPos, minPosIntv, priceUnit)
	else:
		print "\nUnknown strategy '%s'.\n" % options.strategy
		exit()
	
	strategy.run()
	
def strategyAssistant (options, database, table, extra):
	tradeRec = 'dummy'	# Currently, does not support Trade Recording.
	#table = extra.split(',')[0]
	table = futcom.futcodeToDataTable(table)
	#print extra, table
	#table = extra[0]
	strategy = options.strategy
	
	if strategy == 'turtle':
		import strategy.turtle as turtle
		strategy = turtle.Turtle(table, table, tradeRec, database)
	elif strategy == 'turt1':
		import strategy.turt1 as turt1	
		strategy = turt1.Turt1(table, table, tradeRec, database)
	else:
		print "\nUnknown strategy '%s' to do assistant.\n" % strategy
		exit()
		
	strategy.assistant(extra)
		
# Regression subsystem option handler transfering options to actions.
def regressionOptionsHandler (options, args):
	if options.database is None:
		print "\nPlease specify database using '-b'.\n"
		return
	
	database = options.database
	
	if options.list:
		listFutureTables (database, options.filter)
		exit()

	if options.strategy is None:
		print "\nPlease specify a strategy to do regression using '-s'.\n"
		return
	
	if options.assistant:
		if options.extra and options.tables:
			strategyAssistant(options, database, options.tables, options.extra)
		elif options.extra is None:
			print "\nPlease specify extra information by '-e' needed by strategy assistant.\n"
		elif options.tables is None:
			print "\nPlease specify a Future code which needs assistance using '-t'.\n"
			
		# Don't allow assistant option '-a' to be used with other options.
		exit()
			
	regSet = []
	if options.tables:
		regSet = futcom.futcodeSetToDataTables(options.tables.split(','))
	else:
		regSet = possibleRegressionTests(database)
		
	if options.filter:
		regSet = regressionFilter(regSet, options.filter)
		
	#print regSet
	for test in regSet:
		doRegression(options, database, test, options.strategy)
	
# Regression subsystem Option Parser. Called in win.py.
def regressionOptionsParser (parser):
	parser.add_option('-a', '--assistant', action="store_true", dest='assistant', 
			help='Check if match any conditions defined in strategy.')
	parser.add_option('-l', '--list', action="store_true", dest='list', 
			help='List all posssible regression tests.')
	parser.add_option('-t', '--tables', dest='tables', 
			help='Only do regression tests for the Futures listed in this set.')
	parser.add_option('-s', '--strategy', dest='strategy', 
			help='The strategy used to do regression tests.')
	parser.add_option('-f', '--filter', dest='filter', 
			help='Only do regression tests for the Futures matching this filter.')
	parser.add_option('-b', '--database', dest='database', 
			help='The database with which regreesion tests will be done.')
	parser.add_option('-e', '--extra', dest='extra', 
			help='extra informaton, contains details used with other options if needed.')
			
	(options, args) = parser.parse_args()

	regressionOptionsHandler(options, args)
