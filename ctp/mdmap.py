#-*- coding:utf-8 -*-

# Market Data Dict Map.
class MarketDataMap:
	def __init__ (self):
		self.dataDict = {}
		pass
	
	def addMdData (self, instrument, depthMarketData):
		self.dataDict[instrument] = depthMarketData
		pass
	
	def delMdData (self):
		return self.dataDict.pop(instrument)
	
	# Delete the entire Market Data Map.
	def delDataMap (self):
		self.dataDict.clear()
		pass
		
	def updateMdData (self, instrument, depthMarketData):
		self.dataDict[instrument] = depthMarketData
		pass
	
	def getMdData (self, instrument):
		return self.dataDict[instrument]
	