#! /usr/bin/python

import sys
from optparse import OptionParser

import dataMgr.whImporter as IMPORT

parser = OptionParser()

# Importer subsystem option handler transfering options to actions.
def importerHandler (options, args):
	imp = None
	if options.database:
		imp = IMPORT.WenhuaImport(options.database)
	else:
		print "\nPlease specify database using '-b'.\n"
		return
	
	if options.dropTable:
		print "\nDrop '%s' from database '%s'.\n" % (options.dropTable, options.database)
		imp.dropFutureTable(options.dropTable)
	
	if options.mode == 'dir':
		# 'directory' mode, import data records from a data directory to data table.
		directory = options.directory
		table = options.dataTable
		if not directory or not table:
			print "\nPlease specify 'directory' and 'dataTable'\n"
			
		if options.raw:
			imp.processRawRecords(directory)
			
		return imp.importFromDir(directory, table)
		
	elif options.mode == 'file':
		# 'file' mode, import data records from a data file to data table.
		print "\nImporting new records from '%s' to '%s'.\n" % (options.dataFile, options.dataTable)
		
		file = options.dataFile
		table = options.dataTable
		if not file or not table:
			print "\nPlease specify 'dataFile' and 'dataTable'\n"
			
		return imp.newImport(file, table)
		
	elif options.mode == 'append':
		# 'append' mode, only append data records from a data file at the end of data table.
		print "\nAppending records to '%s'.\n" % (options.dataTable)
		
		file = options.dataFile
		table = options.dataTable
		if not file or not table:
			print "\nPlease specify 'dataFile' and 'dataTable'\n"
			
		return imp.appendRecordsOnly(file, table)
		
	elif options.mode == 'update':
		# 'update' mode, update the old records in data table and append the new records at 
		# the end of data talbe using the records in data file.
		print "\nUpdating and appending records to '%s'.\n" % (options.dataTable)
		
		file = options.dataFile
		table = options.dataTable
		if not file or not table:
			print "\nPlease specify 'dataFile' and 'dataTable'\n"
			
		return imp.appendUpdateRecords(file, table)
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
	parser.add_option('-r', '--raw', action="store_false", dest='raw', 
			help='Only used with "-d" if the records are raw in directory.')
	#parser.add_option('-u', action="store_false", dest='appendUpdate', 
			#help='Append records and update the old records to data table.')
	parser.add_option('-m', '--mode', dest='mode', 
			help='Working mode. "dir", "file", "append", "update", etc.')
	parser.add_option('-D', '--dropTable', dest='dropTable', 
			help='Drop a table from database.')
	
	(options, args) = parser.parse_args()

	importerHandler(options, args)

def parseArgs ():
	#print sys.argv[0], sys.argv[1]
	arg1 = sys.argv[1]
	if arg1 == 'importer':
		importerOptionsParser(parser)
	else:
		print "\nUnknown subsystem '%s'. \n" % arg1
	
	return

if __name__ == '__main__':
	#print 'hello WinFuture'
	parseArgs()
