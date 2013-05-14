#! /usr/bin/python

'''
This is the core framework to import data records to data tables.
'''

import sys
from optparse import OptionParser

import dataMgr.whImporter as IMPORT

# Drops all Future tables listed in @tables.
def dropFutureTables (imp, tables):
	tableSet = tables.split(',')
	
	for table in tableSet:
		imp.dropFutureTable(table)
		print "Dropped '%s'. " % table

# Importer subsystem option handler transfering options to actions.
def importerOptionsHandler (options, args):
	imp = None
	if options.database:
		imp = IMPORT.WenhuaImport(options.database)
	else:
		print "\nPlease specify database using '-b'.\n"
		return
	
	if options.dropTable:
		print "\nDropping '%s' from database '%s'...\n" % (options.dropTable, options.database)
		dropFutureTables(imp, options.dropTable)
		
	if options.mode == 'dir':
		# 'directory' mode, import data records from a data directory to data table.
		
		directory = options.directory
		table = options.dataTable
		if not directory or not table:
			print "\nPlease specify 'directory' and 'dataTable'\n"
			return
			
		if options.raw:
			imp.processRawRecords(directory)
			
		print "\nImporting new records from '%s' to '%s'...\n" % (directory, table)
		
		return imp.importFromDir(directory, table)
		
	elif options.mode == 'file':
		# 'file' mode, import data records from a data file to data table.
		
		file = options.dataFile
		table = options.dataTable
		if not file or not table:
			print "\nPlease specify 'dataFile' and 'dataTable'\n"
			return
			
		print "\nImporting new records from '%s' to '%s'...\n" % (file, table)
		
		return imp.newImport(file, table)
		
	elif options.mode == 'append':
		# 'append' mode, only append data records from a data file at the end of data table.
		
		file = options.dataFile
		table = options.dataTable
		if not file or not table:
			print "\nPlease specify 'dataFile' and 'dataTable'\n"
			return
			
		print "\nAppending records to '%s'...\n" % (table)
		
		return imp.appendRecordsOnly(file, table)
		
	elif options.mode == 'update':
		# 'update' mode, update the old records in data table and append the new records at 
		# the end of data talbe using the records in data file.
		
		file = options.dataFile
		table = options.dataTable
		if not file or not table:
			print "\nPlease specify 'dataFile' and 'dataTable'\n"
			return
			
		print "\nUpdating and appending records to '%s'...\n" % (table)
		
		return imp.updateRecordsFromFile(file, table)
		
	elif options.mode == 'export':
		file = options.dataFile
		table = options.dataTable
		if not options.dataTable or not options.extra:
			print "\nPlease specify 'dataTable' and 'extra'\n"
			return
		
		time = options.extra.split(',')
		table = options.dataTable.split(',')
		endDate = 'Now'
		
		#print time, table
		
		if len(table) == 1:
			print "\nPlease specify two data tables like '-t m09,m1309'\n"
			return
			
		if len(time) == 2:
			endDate = time[1]

		print "\nExporting '%s' to '%s' from '%s' to '%s'...\n" % (table[0], table[1], time[0], endDate)
		
		if endDate == 'Now':
			imp.partReimport(table[0], table[1], time[0])
		else:
			imp.partReimport(table[0], table[1], time[0], endDate)
		
	elif options.mode is None:
		return
	else:
		print "\nUn-Supported mode '%s'\n" % options.mode

# Importer subsystem Option Parser.
def importerOptionsParser (parser):
	parser.add_option('-b', '--database', dest='database', 
			help='The database in which operations need to be done.')
	parser.add_option('-f', '--dataFile', dest='dataFile', 
			help='The data file from which to import data records.')
	parser.add_option('-t', '--dataTable', dest='dataTable', 
			help='The data table to which to import data records.')
	parser.add_option('-d', '--directory', dest='directory', 
			help='The directory from which to import data records.')
	parser.add_option('-r', '--raw', action="store_true", dest='raw', 
			help='Only used with "-d" if the records are raw in directory.')
	#parser.add_option('-u', action="store_false", dest='appendUpdate', 
			#help='Append records and update the old records to data table.')
	parser.add_option('-m', '--mode', dest='mode', 
			help='Working mode. "dir", "file", "append", "update", etc.')
	parser.add_option('-D', '--dropTable', dest='dropTable', 
			help='Drop a table from database.')
	parser.add_option('-e', '--extra', dest='extra', 
			help='extra informaton, contains details used with other options if needed.')
			
	(options, args) = parser.parse_args()

	importerOptionsHandler(options, args)
	