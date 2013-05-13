#! /usr/bin/python

import sys
from optparse import OptionParser

import dataMgr.importerParser as importerParser
import dataMgr.dataParser as dataParser
import regression

parser = OptionParser()

def parseArgs ():
	#print sys.argv[0], sys.argv[1]
	arg1 = sys.argv[1]
	if arg1 == 'importer':
		importerParser.importerOptionsParser(parser)
	if arg1 == 'data':
		dataParser.dataOptionsParser(parser)
	elif arg1 == 'regress':
		regression.regressionOptionsParser(parser)
	else:
		print "\nUnknown subsystem '%s'. \n" % arg1
	
	return

if __name__ == '__main__':
	#print 'hello WinFuture'
	parseArgs()
