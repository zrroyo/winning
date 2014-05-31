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
		
	