#-*- coding:utf-8 -*-

'''

'''

from debug import *

#
class DevStat:
	def __init__ (self,
		debug = False,		#调试模式
		):
		self.debug = Debug('DevStat', debug)	#调试接口
		
		self.result = []	#
		self.count = 0	#
		
		self.profit = 0	#
		self.maxDayProfit = -1000000	#
		self.minDayProfit = 1000000	#
		
		#
		self.orderStat = OrderStat(debug)
		
	#
	def storeResult (self, 
		high,	#
		low,	#
		profit,	#
		):
		self.result.append((high, low, profit))
		self.count += 1
		self.debug.dbg('High %s, Low %s, Profit %s, Count %s' % 
				(high, low, profit, self.count))
	
	#
	def statAddProfit (self, 
		profit,	#利润
		):
		self.profit += profit
	
	#
	def statUpdateMaxMinDayProfit (self, 
		profit,	#利润
		time,	#交易日
		):
		newProfit = self.profit + profit
		
		#更新盈利最高点
		if newProfit > self.maxDayProfit:
			self.maxDayProfit = newProfit
			self.debug.dbg('Time %s, Max-day-profit %s' % (time, self.maxDayProfit))
			
		#更新盈利最低点
		if newProfit < self.minDayProfit:
			self.minDayProfit = newProfit
			self.debug.dbg('Time %s, Min-day-profit %s' % (time, self.minDayProfit))
		
	#
	def clear (self,
		profit,	#
		):
		self.storeResult(self.maxDayProfit, self.minDayProfit, profit)
		self.profit = 0
		self.maxDayProfit = -1000000
		self.minDayProfit = 1000000
		
	#
	def showStat (self):
		print self.result
		
		high = [r[0] for r in self.result if r[0] != 0]
		print high
		
		avg = sum(high)/len(high)
		print 'Avg highest %.2f' % avg
		higherAvgProfit = [(r[0], r[2]) for r in self.result if r[0] >= avg]
		print higherAvgProfit, len(higherAvgProfit)
		
		print 'Order Statistics:'
		self.orderStat.showOrderStat()
	
#
class OrderStat:
	
	pos1 = []	#
	pos2 = []
	pos3 = []
	pos4 = []
	pos5 = []
	pos6 = []
	
	current = [0, 0, 0, 0, 0, 0]	#
	#current = []	
	#current[0:5] = 0
	
	def __init__ (self,
		debug = False,		#调试模式
		):
		self.debug = Debug('OrderStat', debug)	#调试接口
		
	#
	def doStatForOrders (self,
		profitList,	#
		):
		self.debug.dbg('profitList %s' % profitList)
		
		idx = 0
		bound = len(profitList)
		
		while idx < bound:
			if profitList[idx] > self.current[idx]:
				self.current[idx] = profitList[idx]
			
			idx += 1
		
		self.debug.dbg('Current %s' % self.current)

	#
	def statPosition (self,
		posNum,	#
		):
		if posNum == 1:
			self.pos1.append(self.current[posNum - 1])
		elif posNum == 2:
			self.pos2.append(self.current[posNum - 1])
		elif posNum == 3:
			self.pos3.append(self.current[posNum - 1])
		elif posNum == 4:
			self.pos4.append(self.current[posNum - 1])
		elif posNum == 5:
			self.pos5.append(self.current[posNum - 1])
		elif posNum == 6:
			self.pos6.append(self.current[posNum - 1])
		
		self.current[posNum - 1] = 0
		
	#
	def showOrderStat (self):
		print self.pos1, len(self.pos1)
		print self.pos2, len(self.pos2)
		print self.pos3, len(self.pos3)
		print self.pos4, len(self.pos4)
		print self.pos5, len(self.pos5)
		print self.pos6, len(self.pos6)
		