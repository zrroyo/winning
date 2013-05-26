#!/usr/bin/python

import sys
sys.path.append('..')

import dataMgr.whImporter as IMPORT

imp = IMPORT.WenhuaImport('history')
print '\nsplit rb01:'
imp.splitTableToSubFutures('rb', 'rb01', 1, 15, 2014, 2003)

print '\nsplit sr01:'
imp.splitTableToSubFutures('sr', 'sr01', 1, 10, 2014, 2003)

print '\nsplit m01:'
imp.splitTableToSubFutures('m', 'm01', 1, 10, 2014, 2003)

print '\nsplit pta01:'
imp.splitTableToSubFutures('m', 'pta01', 1, 10, 2014, 2003)

print '\nsplit P01:'
imp.splitTableToSubFutures('m', 'P01', 1, 10, 2014, 2003)

print '\nsplit fg01:'
imp.splitTableToSubFutures('m', 'fg01', 1, 10, 2014, 2003)


