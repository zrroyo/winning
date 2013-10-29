#-*- coding:utf-8 -*-

import copy
from futures import ApiStruct

# Market Data Dict Map.
class MarketDataMap:
	def __init__ (self):
		self.dataDict = {}
		pass
	
	def addMdData (self, instrument, depthMarketData):
		dp = copy.deepcopy(depthMarketData)
		self.dataDict[instrument] = dp
		pass
	
	def delMdData (self, instrument):
		return self.dataDict.pop(instrument)
	
	# Delete the entire Market Data Map.
	def delDataMap (self):
		self.dataDict.clear()
		pass
		
	def updateMdData (self, instrument, depthMarketData):
		self.addMdData(instrument, depthMarketData)
		pass
	
	def getMdData (self, instrument):
		return self.dataDict[instrument]
	
	def isMdDataExisted (self, instrument):
		if instrument in self.dataDict.keys():
			return True
		else:
			return False
		