#! /usr/bin/python

import sys
sys.path.append('..')
import strategy.turt1 as TURT
import dataMgr.whImporter as IMPORT

imp = IMPORT.WenhuaImport('history')
imp.partReimport('P01', 'P1401_dayk', '2013-1-18')
imp.partReimport('P01', 'P1301_dayk', '2012-1-18', '2013-1-17')
imp.partReimport('P01', 'P1201_dayk', '2011-1-18', '2012-1-16')
imp.partReimport('P01', 'P1101_dayk', '2010-1-18', '2011-1-5')
imp.partReimport('P01', 'P1001_dayk', '2009-1-19', '2010-1-14')
imp.partReimport('P01', 'P0901_dayk', '2008-1-16', '2009-1-13')
imp.partReimport('P01', 'P0801_dayk', '2007-10-29', '2008-1-7')
