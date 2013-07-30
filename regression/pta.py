#!/usr/bin/python

import sys
sys.path.append('..')
import strategy.turt1 as TURT
import dataMgr.whImporter as IMPORT

#imp = IMPORT.WenhuaImport('history')
#table = 'pta09'
##ptaDir = '/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/pta09-test'
##imp.importFromDir(ptaDir, table)

#dataFile = '/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/pta09/pta1309.txt'
##imp.appendUpdateRecords(dataFile, table)

##imp.partReimport(table, 'pta1309_dayk', '2012-09-17')
##imp.partReimport(table, 'pta1209_dayk', '2011-09-16', '2012-09-14')
##imp.partReimport(table, 'pta1109_dayk', '2010-09-15', '2011-09-15')
##imp.partReimport(table, 'pta1009_dayk', '2009-09-16', '2010-09-14')
##imp.partReimport(table, 'pta0909_dayk', '2008-09-16', '2009-09-15')
##imp.partReimport(table, 'pta0809_dayk', '2007-09-19', '2008-09-12')
##imp.partReimport(table, 'pta0709_dayk', '2007-02-26', '2007-09-14')

#minPosIntv=80

#turt = TURT.Turt1('pta0709', 'pta0709_dayk', 'pta0709_dayk_trade_rec', 'history')
#turt.setAttrs(3, 1, minPosIntv, 5)
##turt.atr()
#turt.run()

#turt = TURT.Turt1('pta0809', 'pta0809_dayk', 'pta0809_dayk_trade_rec', 'history')
#turt.setAttrs(3, 1, minPosIntv, 5)
##turt.atr()
#turt.run()

#turt = TURT.Turt1('pta0909', 'pta0909_dayk', 'pta0909_dayk_trade_rec', 'history')
#turt.setAttrs(3, 1, minPosIntv, 5)
##turt.atr()
#turt.run()

#turt = TURT.Turt1('pta1009', 'pta1009_dayk', 'pta1009_dayk_trade_rec', 'history')
#turt.setAttrs(3, 1, minPosIntv, 5)
##turt.atr()
#turt.run()

#turt = TURT.Turt1('pta1109', 'pta1109_dayk', 'pta1109_dayk_trade_rec', 'history')
#turt.setAttrs(3, 1, minPosIntv, 5)
##turt.atr()
#turt.run()

#turt = TURT.Turt1('pta1209', 'pta1209_dayk', 'pta1209_dayk_trade_rec', 'history')
#turt.setAttrs(3, 1, minPosIntv, 5)
##turt.atr()
#turt.run()

#imp.appendRecordsOnly(dataFile, table)
#imp.dropFutureTable('pta1309_dayk')
#imp.partReimport(table, 'pta1309_dayk', '2012-09-17')

#turt = TURT.Turt1('pta1309', 'pta1309_dayk', 'pta1309_dayk_trade_rec', 'history')
#turt.setAttrs(3, 1, minPosIntv, 5)
##turt.atr()
#turt.run()

#imp = IMPORT.WenhuaImport('history')
#imp.partReimport('pta01', 'pta1401_dayk', '2013-1-18')
#imp.partReimport('pta01', 'pta1301_dayk', '2012-1-30', '2013-1-17')
#imp.partReimport('pta01', 'pta1201_dayk', '2011-1-18', '2012-1-20')
#imp.partReimport('pta01', 'pta1101_dayk', '2010-1-18', '2011-1-17')
#imp.partReimport('pta01', 'pta1001_dayk', '2009-2-11', '2010-1-15')
#imp.partReimport('pta01', 'pta0901_dayk', '2008-2-5', '2009-1-20')
#imp.partReimport('pta01', 'pta0801_dayk', '2007-3-19', '2008-1-15')


imp = IMPORT.WenhuaImport('history')
imp.partReimport('pta05', 'pta1405_dayk', '2013-5-16')
imp.partReimport('pta05', 'pta1305_dayk', '2012-5-16', '2013-5-15')
imp.partReimport('pta05', 'pta1205_dayk', '2011-5-16', '2012-5-15')
imp.partReimport('pta05', 'pta1105_dayk', '2010-5-16', '2011-5-15')
imp.partReimport('pta05', 'pta1005_dayk', '2009-5-16', '2010-5-15')
imp.partReimport('pta05', 'pta0905_dayk', '2008-5-16', '2009-5-15')
imp.partReimport('pta05', 'pta0805_dayk', '2007-5-16', '2008-5-15')
imp.partReimport('pta05', 'pta0705_dayk', '2006-5-16', '2007-5-15')
