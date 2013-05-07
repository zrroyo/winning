#!/usr/bin/python

import sys
sys.path.append('..')
import strategy.turt1 as TURT
import dataMgr.whImporter as IMPORT

imp = IMPORT.WenhuaImport('history')
table = 'pta09'
#ptaDir = '/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/pta09-test'
#imp.importFromDir(ptaDir, table)

dataFile = '/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/pta09/pta1309.txt'
#imp.appendUpdateRecords(dataFile, table)

#imp.partReimport(table, 'pta1309_dayk', '2012-09-17')
#imp.partReimport(table, 'pta1209_dayk', '2011-09-16', '2012-09-14')
#imp.partReimport(table, 'pta1109_dayk', '2010-09-15', '2011-09-15')
#imp.partReimport(table, 'pta1009_dayk', '2009-09-16', '2010-09-14')
#imp.partReimport(table, 'pta0909_dayk', '2008-09-16', '2009-09-15')
#imp.partReimport(table, 'pta0809_dayk', '2007-09-19', '2008-09-12')
#imp.partReimport(table, 'pta0709_dayk', '2007-02-26', '2007-09-14')

turt = TURT.Turt1('pta0709', 'pta0709_dayk', 'pta0709_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, 40)
#turt.atr()
turt.run()

turt = TURT.Turt1('pta0809', 'pta0809_dayk', 'pta0809_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, 40)
#turt.atr()
turt.run()

turt = TURT.Turt1('pta0909', 'pta0909_dayk', 'pta0909_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, 40)
#turt.atr()
turt.run()

turt = TURT.Turt1('pta1009', 'pta1009_dayk', 'pta1009_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, 40)
#turt.atr()
turt.run()

turt = TURT.Turt1('pta1109', 'pta1109_dayk', 'pta1109_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, 40)
#turt.atr()
turt.run()

turt = TURT.Turt1('pta1209', 'pta1209_dayk', 'pta1209_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, 40)
#turt.atr()
turt.run()

imp.appendRecordsOnly(dataFile, table)
imp.dropFutureTable('pta1309_dayk')
imp.partReimport(table, 'pta1309_dayk', '2012-09-17')

turt = TURT.Turt1('pta1309', 'pta1309_dayk', 'pta1309_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, 40)
#turt.atr()
turt.run()
