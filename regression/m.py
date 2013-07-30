#!/usr/bin/python

import sys
sys.path.append('..')
import strategy.turt1 as TURT
import dataMgr.whImporter as IMPORT

#imp = IMPORT.WenhuaImport('history')
#table = 'm09'
#dataFile = '/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/m09/m1309.txt'

##imp.appendUpdateRecords(dataFile, table)

##imp.splitTableToSubFutures('m', 'm09', 9, 10, 2012, 2008)

##imp.partReimport('m09', 'm1309_dayk', '2012-09-17')
##imp.partReimport('m09', 'm1209_dayk', '2011-09-16', '2012-09-14')
##imp.partReimport('m09', 'm1109_dayk', '2010-09-14', '2011-09-07')
##imp.partReimport('m09', 'm1009_dayk', '2009-09-15', '2010-09-08')
##imp.partReimport('m09', 'm0909_dayk', '2008-09-16', '2009-09-02')
##imp.partReimport('m09', 'm0809_dayk', '2007-09-17', '2008-09-11')
##imp.partReimport('m09', 'm0709_dayk', '2006-09-21', '2007-09-10')
##imp.partReimport('m09', 'm0609_dayk', '2005-09-21', '2006-09-14')
##imp.partReimport('m09', 'm0509_dayk', '2004-09-15', '2005-09-14')
##imp.partReimport('m09', 'm0409_dayk', '2003-09-15', '2004-09-14')

#minPosIntv=40
#priceUnit=10

#turt = TURT.Turt1('m0409', 'm0409_dayk', '', 'history')
#turt.setAttrs(3, 1, minPosIntv, priceUnit)
##turt.atr()
#turt.run()

#turt = TURT.Turt1('m0509', 'm0509_dayk', '', 'history')
#turt.setAttrs(3, 1, minPosIntv, priceUnit)
##turt.atr()
#turt.run()

#turt = TURT.Turt1('m0609', 'm0609_dayk', '', 'history')
#turt.setAttrs(3, 1, minPosIntv, priceUnit)
##turt.atr()
#turt.run()

#turt = TURT.Turt1('m0709', 'm0709_dayk', '', 'history')
#turt.setAttrs(3, 1, minPosIntv, priceUnit)
##turt.atr()
#turt.run()

#turt = TURT.Turt1('m0809', 'm0809_dayk', '', 'history')
#turt.setAttrs(3, 1, minPosIntv, priceUnit)
##turt.atr()
#turt.run()

#turt = TURT.Turt1('m0909', 'm0909_dayk', '', 'history')
#turt.setAttrs(3, 1, minPosIntv, priceUnit)
##turt.atr()
#turt.run()

#turt = TURT.Turt1('m1009', 'm1009_dayk', '', 'history')
#turt.setAttrs(3, 1, minPosIntv, priceUnit)
##turt.atr()
#turt.run()

#turt = TURT.Turt1('m1109', 'm1109_dayk', '', 'history')
#turt.setAttrs(3, 1, minPosIntv, priceUnit)
##turt.atr()
#turt.run()

#turt = TURT.Turt1('m1209', 'm1209_dayk', '', 'history')
#turt.setAttrs(3, 1, minPosIntv, priceUnit)
##turt.atr()
#turt.run()

#turt = TURT.Turt1('m1309', 'm1309_dayk', '', 'history')
#turt.setAttrs(3, 1, minPosIntv, priceUnit)
#turt.atr()
#turt.run()

#imp = IMPORT.WenhuaImport('history')
#imp.partReimport('m01', 'm1401_dayk', '2013-1-18')
#imp.partReimport('m01', 'm1301_dayk', '2012-1-18', '2013-1-17')
#imp.partReimport('m01', 'm1201_dayk', '2011-1-18', '2012-1-13')
#imp.partReimport('m01', 'm1101_dayk', '2010-1-18', '2011-1-10')
#imp.partReimport('m01', 'm1001_dayk', '2009-1-19', '2010-1-15')
##Note#
#imp.partReimport('m01', 'm0901_dayk', '2008-1-14', '2009-1-16')
##Note#
#imp.partReimport('m01', 'm0801_dayk', '2007-1-19', '2008-1-9')
#imp.partReimport('m01', 'm0701_dayk', '2006-1-18', '2007-1-17')
#imp.partReimport('m01', 'm0601_dayk', '2005-1-18', '2006-1-13')
#imp.partReimport('m01', 'm0501_dayk', '2004-1-29', '2005-1-17')
#imp.partReimport('m01', 'm0401_dayk', '2003-1-16', '2004-1-16')

imp = IMPORT.WenhuaImport('history')
imp.partReimport('m05', 'm1405_dayk', '2013-5-16')
imp.partReimport('m05', 'm1305_dayk', '2012-5-16', '2013-5-15')
imp.partReimport('m05', 'm1205_dayk', '2011-5-16', '2012-5-15')
imp.partReimport('m05', 'm1105_dayk', '2010-5-16', '2011-5-15')
imp.partReimport('m05', 'm1005_dayk', '2009-5-16', '2010-5-15')
imp.partReimport('m05', 'm0905_dayk', '2008-5-16', '2009-5-15')
imp.partReimport('m05', 'm0805_dayk', '2007-5-16', '2008-5-15')
imp.partReimport('m05', 'm0705_dayk', '2006-5-16', '2007-5-15')
imp.partReimport('m05', 'm0605_dayk', '2005-5-16', '2006-5-15')
imp.partReimport('m05', 'm0505_dayk', '2004-5-16', '2005-5-15')
imp.partReimport('m05', 'm0405_dayk', '2003-5-16', '2004-5-15')
