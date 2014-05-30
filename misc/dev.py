#-*- coding:utf-8 -*-

'''

'''

from debug import *

#
class DevStat:
	
	highest = []	#
	highCount = 0	#
	lowest = []	#
	lowCount = 0	#
	
	profit = 0	#
	maxDayProfit = -1000000	#
	minDayProfit = 1000000	#
	
	def __init__ (self,
		debug = False,		#调试模式
		):
		self.debug = Debug('DevStat', debug)	#调试接口
		
	#
	def statHighestLowest (self, 
		high,	#
		low,	#
		):
		self.highest.append(high)
		self.highCount += 1
		self.lowest.append(low)
		self.lowCount += 1
		self.debug.dbg('High %s highCount %s, Low %s lowCount %s' % 
				(high, self.highCount, low, self.lowCount))
	
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
	def clear (self):
		self.profit = 0
		self.statHighestLowest(self.maxDayProfit, self.minDayProfit)
		self.maxDayProfit = -1000000
		self.minDayProfit = 1000000
		
	#
	def showStat (self):
		print self.highest
		
		high = [h for h in self.highest if h != 0]
		print high
		
		print self.lowest
		low = [l for l in self.lowest if l != 0]
		print low
	