#-*- coding:utf-8 -*-

'''
交易数据记录模块(Trading Counter Module)
	Author:　ruan.zhengwang@gmail.com
'''
	
'''
交易数据记录
'''
class TradingCounter:
	def __init__ (self):
		self.numOpen = 0	#开仓数
		self.numClose = 0	#平仓数
		self.numBusWin = 0	#赢利交易数
		self.numBusLoss = 0	#亏损交易数
		self.numBusFlat = 0	#持平交易数
		self.numOrderWin = 0	#赢利单数
		self.numOrderLoss = 0	#亏损单数
		self.numOrderFlat = 0	#持平单数
		self.numTrade = 0	#总交易数
		
	#增加开仓数
	def incNumOpen (self,
		num = 1,	#增加值
		):
		self.numOpen += num
		
	#增加平仓数
	def incNumClose (self,
		num = 1,	#增加值
		):
		self.numClose += num
		
	#增加赢利交易数
	def incNumBusWin (self,
		num = 1,	#增加值
		):
		self.numBusWin += num
		
	#增加亏损交易数
	def incNumBusLoss (self,
		num = 1,	#增加值
		):
		self.numBusLoss += num
		
	#增加持平交易数
	def incNumBusFlat (self,
		num = 1,	#增加值
		):
		self.numBusFlat += num
		
	#增加赢利单数
	def incNumOrderWin (self,
		num = 1,	#增加值
		):
		self.numOrderWin += num
		
	#增加亏损单数
	def incNumOrderLoss (self,
		num = 1,	#增加值
		):
		self.numOrderLoss += num
		
	#增加持平单数
	def incNumOrderFlat (self,
		num = 1,	#增加值
		):
		self.numOrderFlat += num
		
	#增加总交易数
	def incNumTrade (self,
		num = 1,	#增加值
		):
		self.numTrade += num
		
	#赢利交易比
	def busWinRate (self):
		rate = float(self.numBusWin) / self.numTrade * 100
		return '%.2f' % rate
		
	#赢利单比
	def orderWinRate (self):
		rate = float(self.numOrderWin) / self.numOpen * 100
		return '%.2f' % rate
	