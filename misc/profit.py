#-*- coding:utf-8 -*-

'''
利润及回撤模块(Ｐrofit and Regression Module)
	Author:　ruan.zhengwang@gmail.com
'''

import thread

'''
利润及回撤类
'''
class ProfitRegress:
	def __init__ (self,
		debug = False,		#调试模式
		numInstruments = 2,	#并行执行的合约数量
		):
		self.profit = 0		#当前利润
		self.maxProfit = 0	#盈利最高点
		self.minProfit = 0	#盈利最低点
		self.debug = debug
		self.numInstruments = numInstruments
		
		self.lock = thread.allocate_lock()	#保护锁，保护整个数据结构
		self.dynamicProfit = 0	#动态利润统计
		self.countTimes = 0	#已统计的合约数
		
	#打印调试信息
	def dbg (self,
		dbgInfo,	#debug信息
		):
		if self.debug:
			print '	ProfitRegress: %s' % dbgInfo
		
	#更新最大最小利润
	def updateMaxMinProfit (self, 
		profit,	#利润
		time,	#交易日
		):
		self.lock.acquire()
		if self.countTimes != self.numInstruments - 1:
			self.dynamicProfit = profit
			self.countTimes += 1
			self.lock.release()
			return
		
		self.dynamicProfit += profit
		newProfit = self.profit + self.dynamicProfit
		self.dbg('Time %s, newProfit %s, profit1 %s, profit2 %s, profit %s' % 
				(time, newProfit, self.dynamicProfit - profit, profit, self.profit))
		self.dynamicProfit = 0
		self.countTimes = 0
		self.lock.release()
		
		#更新盈利最高点
		if newProfit > self.maxProfit:
			self.maxProfit = newProfit
			self.dbg('Time %s, Max profit %s' % (time, self.maxProfit))
			
		#更新盈利最低点
		if newProfit < self.minProfit:
			self.minProfit = newProfit
			self.dbg('Time %s, Min profit %s' % (time, self.minProfit))
			
	#更新利润(以交易单为单位)
	def updateProfitByOrder (self, 
		profit,	#利润
		):
		#更新当前利润
		self.profit += profit
			
		self.dbg('Current profit %s, profit %s, Max profit %s' % 
					(self.profit - profit, profit, self.maxProfit))
		
		#更新盈利最高点
		if self.profit > self.maxProfit:
			self.maxProfit = self.profit
			self.dbg('Max profit %s' % self.maxProfit)
			
		#更新盈利最低点
		if self.profit < self.minProfit:
			self.minProfit = self.profit
			self.dbg('Min profit %s' % self.minProfit)
		