#!/usr/bin/python

import sys
sys.path.append('..')
import strategy.turt1 as TURT
import dataMgr.whImporter as IMPORT

imp = IMPORT.WenhuaImport('history')
table = 'm09'
dataFile = '/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/m09/m1309.txt'

#imp.appendUpdateRecords(dataFile, table)

#imp.splitTableToSubFutures('m', 'm09', 9, 10, 2012, 2008)

#imp.partReimport('m09', 'm1309_dayk', '2012-09-17')
#imp.partReimport('m09', 'm1209_dayk', '2011-09-16', '2012-09-14')
#imp.partReimport('m09', 'm1109_dayk', '2010-09-14', '2011-09-07')
#imp.partReimport('m09', 'm1009_dayk', '2009-09-15', '2010-09-08')
#imp.partReimport('m09', 'm0909_dayk', '2008-09-16', '2009-09-02')
#imp.partReimport('m09', 'm0809_dayk', '2007-09-17', '2008-09-11')
#imp.partReimport('m09', 'm0709_dayk', '2006-09-21', '2007-09-10')
#imp.partReimport('m09', 'm0609_dayk', '2005-09-21', '2006-09-14')
#imp.partReimport('m09', 'm0509_dayk', '2004-09-15', '2005-09-14')
#imp.partReimport('m09', 'm0409_dayk', '2003-09-15', '2004-09-14')

minPosIntv=40
priceUnit=10

turt = TURT.Turt1('m0409', 'm0409_dayk', '', 'history')
turt.setAttrs(3, 1, minPosIntv, priceUnit)
#turt.atr()
turt.run()

turt = TURT.Turt1('m0509', 'm0509_dayk', '', 'history')
turt.setAttrs(3, 1, minPosIntv, priceUnit)
#turt.atr()
turt.run()

turt = TURT.Turt1('m0609', 'm0609_dayk', '', 'history')
turt.setAttrs(3, 1, minPosIntv, priceUnit)
#turt.atr()
turt.run()

turt = TURT.Turt1('m0709', 'm0709_dayk', '', 'history')
turt.setAttrs(3, 1, minPosIntv, priceUnit)
#turt.atr()
turt.run()

turt = TURT.Turt1('m0809', 'm0809_dayk', '', 'history')
turt.setAttrs(3, 1, minPosIntv, priceUnit)
#turt.atr()
turt.run()

turt = TURT.Turt1('m0909', 'm0909_dayk', '', 'history')
turt.setAttrs(3, 1, minPosIntv, priceUnit)
#turt.atr()
turt.run()

turt = TURT.Turt1('m1009', 'm1009_dayk', '', 'history')
turt.setAttrs(3, 1, minPosIntv, priceUnit)
#turt.atr()
turt.run()

turt = TURT.Turt1('m1109', 'm1109_dayk', '', 'history')
turt.setAttrs(3, 1, minPosIntv, priceUnit)
#turt.atr()
turt.run()

turt = TURT.Turt1('m1209', 'm1209_dayk', '', 'history')
turt.setAttrs(3, 1, minPosIntv, priceUnit)
#turt.atr()
turt.run()

turt = TURT.Turt1('m1309', 'm1309_dayk', '', 'history')
turt.setAttrs(3, 1, minPosIntv, priceUnit)
turt.atr()
turt.run()
