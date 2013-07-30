#!/usr/bin/python

import sys
sys.path.append('..')
import strategy.turt1 as TURT
import dataMgr.whImporter as IMPORT

imp = IMPORT.WenhuaImport('history')
table = 'sr09'
dateFile = '/media/Work/ubuntu/VirtualBox/shareDir/Data/Futures/wenhua/dayk/history/sr09/sr1309.txt'

#imp.appendUpdateRecords(dateFile, table)

##imp.splitTable('sr', 'sr09', 2013, 9, 10)

#imp.partReimport(table, 'sr1309_dayk', '2012-09-17')
#imp.partReimport(table, 'sr1209_dayk', '2012-03-15', '2012-09-14')
#imp.partReimport(table, 'sr1109_dayk', '2010-09-15', '2011-09-15')
#imp.partReimport(table, 'sr1009_dayk', '2010-03-15', '2010-09-14')
#imp.partReimport(table, 'sr0909_dayk', '2008-09-16', '2009-09-14')
#imp.partReimport(table, 'sr0809_dayk', '2008-05-19', '2008-09-12')
#imp.partReimport(table, 'sr0709_dayk', '2006-09-15', '2007-09-14')
#imp.partReimport(table, 'sr0609_dayk', '2006-01-06', '2006-09-08')

#turt = TURT.Turt1('sr0609', 'sr0609_dayk', '', 'history')
##turt.atr()
#turt.setAttrs(3, 1, 40)
#turt.run()

#turt = TURT.Turt1('sr0709', 'sr0709_dayk', '', 'history')
##turt.atr()
#turt.setAttrs(3, 1, 40)
#turt.run()

#turt = TURT.Turt1('sr0809', 'sr0809_dayk', '', 'history')
##turt.atr()
#turt.setAttrs(3, 1, 40)
#turt.run()

#turt = TURT.Turt1('sr0909', 'sr0909_dayk', '', 'history')
##turt.atr()
#turt.setAttrs(3, 1, 40)
#turt.run()

#turt = TURT.Turt1('sr1009', 'sr1009_dayk', '', 'history')
##turt.atr()
#turt.setAttrs(3, 1, 40)
#turt.run()

#turt = TURT.Turt1('sr1109', 'sr1109_dayk', '', 'history')
##turt.atr()
#turt.setAttrs(3, 1, 40)
#turt.run()

#turt = TURT.Turt1('sr1209', 'sr1209_dayk', '', 'history')
##turt.atr()
#turt.setAttrs(3, 1, 40)
#turt.run()

#turt = TURT.Turt1('sr1309', 'sr1309_dayk', '', 'history')
##turt.atr()
#turt.setAttrs(3, 1, 40)
#turt.run()

#imp = IMPORT.WenhuaImport('history')
#imp.partReimport('sr05', 'sr1405_dayk', '2013-5-16')
#imp.partReimport('sr05', 'sr1305_dayk', '2012-5-16', '2013-5-15')
#imp.partReimport('sr05', 'sr1205_dayk', '2011-5-16', '2012-5-15')
#imp.partReimport('sr05', 'sr1105_dayk', '2010-5-16', '2011-5-15')
#imp.partReimport('sr05', 'sr1005_dayk', '2009-5-16', '2010-5-15')
#imp.partReimport('sr05', 'sr0905_dayk', '2008-5-16', '2009-5-15')
#imp.partReimport('sr05', 'sr0805_dayk', '2007-5-16', '2008-5-15')
#imp.partReimport('sr05', 'sr0705_dayk', '2006-5-16', '2007-5-15')
#imp.partReimport('sr05', 'sr0605_dayk', '2005-5-16', '2006-5-15')

imp = IMPORT.WenhuaImport('history')
imp.partReimport('sr01', 'sr1401_dayk', '2013-1-16')
imp.partReimport('sr01', 'sr1301_dayk', '2012-1-16', '2013-1-15')
imp.partReimport('sr01', 'sr1201_dayk', '2011-1-16', '2012-1-15')
imp.partReimport('sr01', 'sr1101_dayk', '2010-1-16', '2011-1-15')
imp.partReimport('sr01', 'sr1001_dayk', '2009-1-16', '2010-1-15')
imp.partReimport('sr01', 'sr0901_dayk', '2008-1-16', '2009-1-15')
imp.partReimport('sr01', 'sr0801_dayk', '2007-1-16', '2008-1-15')
imp.partReimport('sr01', 'sr0701_dayk', '2006-1-16', '2007-1-15')
imp.partReimport('sr01', 'sr0601_dayk', '2005-1-16', '2006-1-15')