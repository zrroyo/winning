#-*- coding:utf-8 -*-

'''
将行情数据转换为本地数据
'''

import sys
sys.path.append('..')
from misc.elemmap import ElementMap

#行情数据访问接口
class MarketDataAccess:
	def __init__ (self, 
		elemMap,	#行情数据（元素映射）
		logOnErr=False	#遇错需提示
		):
		self.elemMap = elemMap
		self.logOnErr = logOnErr
		
	#得到开盘价
	def getOpen (self, instrument):
		try:
			dp = self.elemMap.getElement(instrument)
			return int(dp.OpenPrice)
		except:
			if self.logOnErr:
				print 'MarketDataAccess:getOpen error'
			return None
			
	#得到收盘价
	def getClose (self, instrument):
		try:
			dp = self.elemMap.getElement(instrument)
			return int(dp.LastPrice)
		except:
			if self.logOnErr:
				print 'MarketDataAccess:getClose error'
			return None
			
	#得到最高价
	def getHighest (self, instrument):
		try:
			dp = self.elemMap.getElement(instrument)
			return int(dp.HighestPrice)
		except:
			if self.logOnErr:
				print 'MarketDataAccess:getHighest error'
			return None
			
	#得到最低价
	def getLowest (self, instrument):
		try:
			dp = self.elemMap.getElement(instrument)
			return int(dp.LowestPrice)
		except:
			if self.logOnErr:
				print 'MarketDataAccess:getLowest error'
			return None
			
	#得到成交量
	def getVolume (self, instrument):
		try:
			dp = self.elemMap.getElement(instrument)
			return int(dp.Volume)
		except:
			if self.logOnErr:
				print 'MarketDataAccess:getVolume error'
			return None
			
	#得到申买价一
	def getBidPrice1 (self, instrument):
		try:
			dp = self.elemMap.getElement(instrument)
			return int(dp.BidPrice1)
		except:
			if self.logOnErr:
				print 'MarketDataAccess:getBidPrice1 error'
			return None
			
	#得到申卖价一
	def getAskPrice1 (self, instrument):
		try:
			dp = self.elemMap.getElement(instrument)
			return int(dp.AskPrice1)
		except:
			if self.logOnErr:
				print 'MarketDataAccess:getAskPrice1 error'
			return None
			
	#得到最新更新时间
	def getUpdateTime (self, instrument):
		try:
			dp = self.elemMap.getElement(instrument)
			return dp.UpdateTime
		except:
			if self.logOnErr:
				print 'MarketDataAccess:getUpdateTime error'
			return None
			