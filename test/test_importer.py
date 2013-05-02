#! /usr/bin/python

import sys
sys.path.append("..")
#import dataMgr.importer as IMPORT
#imp = IMPORT.Import('../tmp/dayk/rb09.txt', 'rb09_dayk')

import dataMgr.whImporter as WHIMPORT
#imp = WHIMPORT.WenhuaImport()
#imp.newImport('../tmp/dayk/rb09.txt', 'rb09_dayk')
#imp.newImport('../tmp/dayk/rb09.txt-bak', 'rb09_dayk_bak')
#imp.partReimport('rb09_dayk', 'rb09_test', '2013-02-04', '2013-03-08')
#imp.partReimport('rb09_dayk', 'rb09_test_2', '2012-09-18')

#imp.importFromDir('/media/Work/mySpace/Dev/WinFuture/Data/futures/rb09', 'rb09')


imp = WHIMPORT.WenhuaImport('history')
#imp.processRawRecords('/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/rb10-test')
#imp.importFromDir('/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/rb10-test', 'rb10')

##imp.processRawRecords('/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/m09-test')
##imp.importFromDir('/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/m09-test', 'm09')

#imp.processRawRecords('/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/sr09-test')
#imp.importFromDir('/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/sr09-test', 'sr09')

#imp.processRawRecords('/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/pta09-test')
#imp.importFromDir('/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/pta09-test', 'pta09')

##imp = WHIMPORT.WenhuaImport('history')
#datafile = '/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/rb10/rb1310.txt'
#datatable = 'rb10'
##imp.appendRecordsOnly(datafile, datatable)
#imp.appendUpdateRecords(datafile, datatable)

imp.tableNameTemplate('pta', 2007, 9)
imp.tableNameTemplate('pta', 2012, 12)
