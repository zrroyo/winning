#! /usr/bin/python

import sys
sys.path.append("..")
#import dataMgr.importer as IMPORT
#imp = IMPORT.Import('../tmp/dayk/rb09.txt', 'rb09_dayk')

import strategy.turt1 as TURT
import dataMgr.whImporter as WHIMPORT
#imp = WHIMPORT.WenhuaImport()
#imp.newImport('../tmp/dayk/rb09.txt', 'rb09_dayk')
#imp.newImport('../tmp/dayk/rb09.txt-bak', 'rb09_dayk_bak')
#imp.partReimport('rb09_dayk', 'rb09_test', '2013-02-04', '2013-03-08')
#imp.partReimport('rb09_dayk', 'rb09_test_2', '2012-09-18')

#imp.importFromDir('/media/Work/mySpace/Dev/WinFuture/Data/futures/rb09', 'rb09')


#imp = WHIMPORT.WenhuaImport('history')
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

#imp = WHIMPORT.WenhuaImport('futures')
##print imp.tableNameTemplate('pta', 2007, 9)
##print imp.tableNameTemplate('pta', 2012, 12)

#imp.splitTable('m', 'm1305_day_k', 2013, 5, 10)

#turt = TURT.Turt1('m1305', 'm1305_dayk', 'm1305_dayk_trade_rec')
#turt.atr()

imp = WHIMPORT.WenhuaImport('history')

#imp.splitTable('m', 'm09', 2013, 9, 10)
imp.splitTable('sr', 'sr09', 2013, 9, 10)


