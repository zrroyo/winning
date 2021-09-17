#! /usr/bin/env python
#-*- coding:utf-8 -*-

import sys
from optparse import OptionParser

from dataMgr.importerParser import importerOptionsParser
from dataMgr.dataParser import dataOptionsParser
from core.regressionParser import regressionOptionsParser
from core.draw import drawOptionsParser
# from ctp.ctpParser import ctpOptionsParser

parser = OptionParser()

def parseArgs ():
	#print sys.argv[0], sys.argv[1]
	arg1 = sys.argv[1]
	if arg1 == 'importer':
		importerOptionsParser(parser)
	elif arg1 == 'data':
		dataOptionsParser(parser)
	elif arg1 == 'regress':
		regressionOptionsParser(parser, sys.argv)
	elif arg1 == 'draw':
		drawOptionsParser(parser, sys.argv)
	# elif arg1 == 'ctp':
	# 	ctpOptionsParser(parser)
	else:
		print "\n未知子系统'%s'，请指定正确子系统名称. \n" % arg1
	
	return

if __name__ == '__main__':
	#print 'hello WinFuture'
	parseArgs()
