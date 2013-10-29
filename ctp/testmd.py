#! /usr/bin/python

from futures import ApiStruct
import mdmap

def doTest():
	dataMap = mdmap.MarketDataMap()
	
	dp = ApiStruct.DepthMarketData()
	dp.InstrumentID = 'rb1401'
	dataMap.addMdData(dp.InstrumentID, dp)
	print dataMap.dataDict

	print dataMap.getMdData('rb1401')

	dp.InstrumentID = 'm1401'
	dataMap.addMdData('rb1401', dp)
	print dataMap.dataDict
	
	print dataMap.isMdDataExisted('rb1401')
	
	dataMap.delMdData('rb1401')
	print dataMap.dataDict
	
	dataMap.delDataMap()
	print
	
	pass


if __name__ == '__main__':
	doTest()