#!/usr/bin/python

import sys
sys.path.append('..')
import strategy.turt1 as TURT
import dataMgr.whImporter as IMPORT
import dataMgr.data as data

#
imp = IMPORT.WenhuaImport('history')
dataTable = 'rb10'
dataFile = '/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/rb10/rb1310.txt'
recDir = '/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/rb10-test'

#imp.importFromDir(recDir, dataTable)

##Partly imported manually.
#imp.dropFutureTable('rb1310_dayk')
#imp.dropFutureTable('rb1210_dayk')
#imp.dropFutureTable('rb1110_dayk')
#imp.dropFutureTable('rb1010_dayk')
#imp.dropFutureTable('rb0910_dayk')
#imp.partReimport('rb10', 'rb1310_dayk', '2012-10-16')
#imp.partReimport('rb10', 'rb1210_dayk', '2011-10-18', '2012-10-15')
#imp.partReimport('rb10', 'rb1110_dayk', '2010-10-18', '2011-10-17')
#imp.partReimport('rb10', 'rb1010_dayk', '2009-10-16', '2010-10-15')
#imp.partReimport('rb10', 'rb0910_dayk', '2009-3-27', '2009-10-15')

## Split RB10 into each table by Year.
#imp.splitTableToSubFutures('rb', 'rb10', 10, 15, 2013)

minPosIntv=40

turt = TURT.Turt1('rb0910', 'rb0910_dayk', 'rb0910_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, minPosIntv, 10)
turt.run()

turt = TURT.Turt1('rb1010', 'rb1010_dayk', 'rb1010_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, minPosIntv, 10)
turt.run()

turt = TURT.Turt1('rb1110', 'rb1110_dayk', 'rb1110_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, minPosIntv, 10)
turt.run()

turt = TURT.Turt1('rb1210', 'rb1210_dayk', 'rb1210_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, minPosIntv, 10)
turt.run()

imp.appendRecordsOnly(dataFile, 'rb10')
imp.dropFutureTable('rb1310_dayk')
imp.partReimport('rb10', 'rb1310_dayk', '2012-10-16')

turt = TURT.Turt1('rb1310', 'rb1310_dayk', 'rb1310_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, minPosIntv, 10)
turt.atr()
turt.run()

#dat = data.Data('history', 'rb1310_dayk')
##print dat.lowestBeforeDate('2013-05-07', 10)
#time = '2013-05-07'
#print 'lowest close up to %s : ' % time, dat.lowestUpToDate(time, 9)
#print 'highest close up to %s : ' % time, dat.highestUpToDate(time, 9)
