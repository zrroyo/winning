#! /usr/bin/python

'''
This is the core framework to quickly check data records for Futures.
'''

import sys
sys.path.append('..')

from optparse import OptionParser

import data
import db.mysqldb as sql
import futcom

# Format and print values.
def formatPrint (date, comment, value):
	print '	%s: %s:	%s' % (date, comment, value)

def printMoving (data, date, moving):
	args = moving.split(',')
	#print args
	if len(args) < 2:
		print "\nPlease specify a value for '-m' as 'Close,5'.\n"
		exit()
		
	#print args[1].isdigit()
	if not args[1].isdigit():
		print "\nPlease specify a value for '-m' as 'Close,5'.\n"
		exit()
	
	field = args[0]
	days = int(args[1])
	
	formatPrint(date, '[%s] M%s' % (field, days), data.M(date, field, days))	

# Format and print a data record in database.
def printRecord (record):
	print '		', record

# Print data records within @days up to @date.
def printRecent (database, table, date, days):
	if not days.isdigit():
		print "\nPlease specify a integer value for '-r'.\n"
		exit()
	
	db = sql.MYSQL("localhost", 'win', 'winfwinf', database)
	db.connect()
	
	sqls = 'select * from %s where Time <= "%s" order by Time desc limit %s' % (table, date, days)
	#print sqls
	recs = db.execSql(sqls)
	res = db.fetch('all')
	
	print '	%s: recent %s records:' % (date, days)
	
	i = 0
	while (recs > 0):
		printRecord (res[i])
		i += 1
		recs -= 1

# Print a data record field.
def printField (data, date, field):
	formatPrint(date, '[%s]' % field, data.M(date, field, 1))

# Print the highest value for a field with some days.
def printHighest (data, date, highest):
	args = highest.split(',')
	if len(args) < 2:
		print "\nPlease specify a value for '-H' as 'Close,5'.\n"
		exit()
		
	if not args[1].isdigit():
		print "\nPlease specify a value for '-H' as 'Close,5'.\n"
		exit()
	
	field = args[0]
	days = int(args[1])
		
	formatPrint(date, '[%s] Highest with %s days' % (field, days), data.highestUpToDate(date, days, field))

# Print the lowest value for a field with some days.
def printLowest (data, date, lowest):
	args = lowest.split(',')
	if len(args) < 2:
		print "\nPlease specify a value for '-L' as 'Close,5'.\n"
		exit()
		
	if not args[1].isdigit():
		print "\nPlease specify a value for '-L' as 'Close,5'.\n"
		exit()
	
	field = args[0]
	days = int(args[1])
			
	formatPrint(date, '[%s] Lowest with %s days' % (field, days), data.lowestUpToDate(date, days, field))
	
# Get the first and last data record in data table.	
def getFirstLastRecords (database, table):
	db = sql.MYSQL("localhost", 'win', 'winfwinf', database)
	db.connect()
	
	# Get first record.
	sqls = 'select * from %s order by Time asc limit 1' % (table)
	#print sqls
	recs = db.execSql(sqls)
	res = db.fetch('all')
	print '	%s First record:' % table
	printRecord(res[0])
		
	# Get last record.
	sqls = 'select * from %s order by Time desc limit 1' % (table)
	#print sqls
	recs = db.execSql(sqls)
	res = db.fetch('all')
	
	print '	%s Last record:' % table
	printRecord(res[0])

# Data subsystem option handler transfering options to actions.
def dataOptionsHandler (options, args):
	database = options.database
	table = options.dataTable
	
	if database is None or table is None:
		print "\nPlease specify database ('-b') and datatable ('-t').\n"
		return
	
	# Try to find the passed table in database, otherwise it may cause run error.
	if futcom.futureTalbeExists(table, database) == False:
		table = futcom.futcodeToDataTable(table)
		if futcom.futureTalbeExists(table, database) == False:
			print "\nCan not find any table matching '%s', exit...\n" % options.dataTable
			exit()
	#print table
	
	if options.check:
		getFirstLastRecords (database, table)
		return
	
	if options.date is None:
		print "\nPlease specify the date using '-d'.\n"
		return
		
	date = options.date
	dat = data.Data(database, table)
	
	if options.moving:
		printMoving(dat, date, options.moving)
		
	if options.field:
		printField(dat, date, options.field)
			
	if options.highest:
		printHighest(dat, date, options.highest)
		
	if options.lowest:
		printLowest(dat, date, options.lowest)
		
	if options.recent:
		printRecent(database, table, date, options.recent)
		
# Data subsystem Option Parser.
def dataOptionsParser (parser):
	parser.add_option('-b', '--database', dest='database', 
			help='The database in which operations need to be done.')
	parser.add_option('-t', '--dataTable', dest='dataTable', 
			help='The data table to which to import data records.')
	parser.add_option('-c', '--check', action="store_true", dest='check', 
			help='Check the first and last records in data table.')
	parser.add_option('-d', '--date', dest='date', 
			help='The date in which you want to get data.')
	parser.add_option('-m', '--moving', dest='moving', 
			help='Get the moving average value.')
	parser.add_option('-r', '--recent', dest='recent', 
			help='Get recent records within days.')
	parser.add_option('-f', '--field', dest='field', 
			help='Get a field, such Open, Close, Highest, Lowest, etc.')
	parser.add_option('-H', '--highest', dest='highest', 
			help='Get the highest value for a field within days.')
	parser.add_option('-L', '--lowest', dest='lowest', 
			help='Get the lowest value for a field within days.')
			
	(options, args) = parser.parse_args()
	
	dataOptionsHandler(options, args)
			