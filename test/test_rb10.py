#!/usr/bin/python

import sys
sys.path.append('..')
import strategy.turt1 as TURT
import dataMgr.whImporter as IMPORT

#
#imp = IMPORT.WenhuaImport('history')

# Split RB10 into each table by Year.
#imp.partReimport('rb10', 'rb1310_dayk', '2012-10-16')
#imp.partReimport('rb10', 'rb1210_dayk', '2011-10-18', '2012-10-15')
#imp.partReimport('rb10', 'rb1110_dayk', '2010-10-18', '2011-10-17')
#imp.partReimport('rb10', 'rb1010_dayk', '2009-10-16', '2010-10-15')
#imp.partReimport('rb10', 'rb1010_dayk', '2009-10-16', '2010-10-15')
#imp.partReimport('rb10', 'rb0910_dayk', '2009-3-27', '2009-10-15')

turt = TURT.Turt1('rb1310', 'rb1310_dayk', 'rb1310_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, 40)
turt.run()

turt.atr()

turt = TURT.Turt1('rb1210', 'rb1210_dayk', 'rb1210_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, 40)
turt.run()

turt = TURT.Turt1('rb1110', 'rb1110_dayk', 'rb1110_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, 40)
turt.run()

turt = TURT.Turt1('rb1010', 'rb1010_dayk', 'rb1010_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, 40)
turt.run()

turt = TURT.Turt1('rb0910', 'rb0910_dayk', 'rb0910_dayk_trade_rec', 'history')
turt.setAttrs(3, 1, 40)
turt.run()
