#! /usr/bin/python
#-*- coding:utf-8 -*-

'''
This is the core framework to run regression tests.
'''

import sys
from optparse import OptionParser
import string
import db.mysqldb as sql
import tick
import thread
from misc.runstat import *
from misc.runctrl import *
from regress.emulate import *
from misc.futcom import *
from misc.debug import *

debug = Debug('Regression', False)    #默认关闭debug信息

# List all possible regression tests in database.
def listFutureTables (database, filter):
	regSet = possibleRegressionTests(database)
	if filter is not None:
		regSet = filtering(regSet, filter)
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

#解析合约参数
def parseAttributes (
	attrs,	#参数字串，用'，'分隔
	):
	args = attrs.split(',')

	maxAddPos = int(args[0])
	minPos = int(args[1])
	priceUnit= int(args[3])
	
	if args[2] is '':
		minPosIntv = None
	else:
		minPosIntv= int(args[2])
		
	debug.dbg('Parsed Atrributes: maxAddPos %s, minPos %s, minPosIntv %s, priceUnit %s' % 
					(maxAddPos,minPos,minPosIntv,priceUnit))
	return maxAddPos,minPos,minPosIntv,priceUnit
	
# Core function to do regression for @test with @strategy.
def doRegression (options, database, test, strategy):
	if strategy == 'turt1':
		if options.extra:
			try:
				maxAddPos,minPos,minPosIntv,priceUnit = parseAttributes(options.extra)
			except:
				debug.error("Extra imformation contains incomplete or wrong attributes for Turt1 strategy.")
				exit()
			
		from strategy.turt1 import Turt1
		runStat = RunStat(test)
		strategy = Turt1(test, test, 'dummy', database, runStat)
		strategy.setAttrs(maxAddPos, minPos, minPosIntv, priceUnit)
	else:
		debug.error("Unknown strategy '%s'." % options.strategy)
		exit()
	
	# Run regression test.
	strategy.run()
	# Show the run time statistics at the end of execution.
	if strategy.runStat is not None:
		strategy.runStat.showStat()
	
# Do regressions for a set of or all possible tables.
def doAllRegressions (options, database):
	regSet = []
	if options.tables:
		regSet = futcodeSetToDataTables(options.tables.split(','))
	else:
		regSet = possibleRegressionTests(database)
		
	if options.filter:
		regSet = filtering(regSet, options.filter)
		
	#print regSet
	for test in regSet:
		doRegression(options, database, test, options.strategy)
			
# Do assistant provided by strategies.
def strategyAssistant (options, database):
	if options.extra is None or options.tables is None:
		debug.error("Please specify extra information by '-e' and tables '-t'...")
		exit()
			
	tradeRec = 'dummy'	# Currently, does not support Trade Recording.
	table = futcodeToDataTable(options.tables)
	strategy = options.strategy
	
	if strategy == 'turtle':
		from strategy.turtle import Turtle
		strategy = Turtle(table, table, tradeRec, database)
	elif strategy == 'turt1':
		from strategy.turt1 import Turt1
		strategy = Turt1(table, table, tradeRec, database)
	else:
		debug.error("Unknown strategy '%s' to do assistant." % strategy)
		exit()
		
	strategy.assistant(options.extra)
		
# Do emulation for a set of or all possible tables.
def doEmulation(options, database):
	# Check extra info is filled.
	extra = options.extra.split(',')
	if options.extra is None or len(extra) != 7:
		debug.error("\nPlease specify extra information by '-e' with format like 'maxAddPos,minPos,minPosIntv,priceUnit,maxAllowedPos,startTick1,startTick2'\n")
		exit()
		
	print extra
			
	# Prepare emulation tables set.
	emuSet = []
	if options.tables:
		emuSet = futcodeSetToDataTables(options.tables.split(','))
	else:
		emuSet = possibleRegressionTests(database)
		
	if options.filter:
		emuSet = filtering(emuSet, options.filter)
			
	# Do emulation in a reverse order for tables set.
	emuSet.reverse()
	
	# Prepare run-time control blocks below.
	
	# Fill common attributes.
	maxAddPos = int(extra[0])
	minPos = int(extra[1])
	priceUnit= int(extra[3])
	
	if extra[2] is '':
		minPosIntv = None
	else:
		minPosIntv= int(extra[2])
		
	maxAllowedPos = int(extra[4])
	startTick1 = extra[5]
	startTick2 = extra[6]
			
	# Initialise run-time control blocks.
	comAttr = CommonAttrs(maxAddPos, minPos, minPosIntv, priceUnit)
	runCtrl1 = RunControl(False, thread.allocate_lock(), None, comAttr, False)
	runCtrl2 = RunControl(False, thread.allocate_lock(), None, comAttr, False, startTick2)
	
	# Initialise tick source.
	tickSrc = tick.Tick()
	tickSrc.setCurTick(startTick1)
	
	runCtrlSet = RunCtrlSet(maxAllowedPos, tickSrc)
	runCtrlSet.add(runCtrl1)
	runCtrlSet.add(runCtrl2)
	
	runCtrlSet.enableMarketRunStat()
	
	emu = Emulate(options.strategy, runCtrlSet, emuSet, 
			emulationThreadStart,	#模拟线程入口地址
			database=database	#存放模拟数据的数据库
			)
	emu.run()
		
# Regression subsystem option handler transfering options to actions.
def regressionOptionsHandler (options, args):
	if options.database is None:
		debug.error("Please specify database using '-b'.")
		return
	
	database = options.database
	
	if options.list:
		listFutureTables (database, options.filter)
		exit()

	if options.strategy is None:
		debug.error("Please specify a strategy to do regression using '-s'.")
		return
	
	if options.mode == 'assis':
		strategyAssistant(options, database)
		# Don't allow assistant option '-a' to be used with other options.
		#exit()
	elif options.mode == 'emul':
		doEmulation(options, database)
	else:
		doAllRegressions(options, database)
	
# Regression subsystem Option Parser. Called in win.py.
def regressionOptionsParser (parser):
	parser.add_option('-m', '--mode', dest='mode', 
			help='Regression mode, such as, assis[tant], emu[late], regression.')
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
