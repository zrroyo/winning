#!/usr/bin/python

import sys
sys.path.append('..')
import strategy.turt1 as TURT
import dataMgr.whImporter as IMPORT

imp = IMPORT.WenhuaImport('history')
table = 'm09'
dataFile = '/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/m09/m1309.txt'

#imp.appendUpdateRecords(dataFile, table)

imp.splitTableToSubFutures('m', 'm09', 9, 10, 2013, 2010)