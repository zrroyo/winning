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
			self.dynamicProfit += profit
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
		
'''
一次完整交易的利润及回撤类
'''
class BusinessProfitRegress:
	def __init__ (self,
		debug = False,	#调试模式
		):
		self.debug = debug
		self.lock = thread.allocate_lock()	#保护锁，保护整个数据结构
		self.busProfit = 0			#当前交易的利润
		self.maxBusProfit = 0			#单次完整交易最高盈利
		self.minBusProfit = 0			#单次完整交易最低盈利
	
	#打印调试信息
	def dbg (self,
		dbgInfo,	#debug信息
		):
		if self.debug:
			print '	BusinessProfitRegress: %s' % dbgInfo
	
	#累积利润
	def addProfit (self,
		profit,	#利润
		):
		self.lock.acquire()
		self.busProfit += profit
		self.lock.release()
	
	#利润清零
	def clearProfit (self):
		self.lock.acquire()
		self.busProfit = 0
		self.lock.release()
		
	#得到当前利润
	def getBusProfit (self):
		return self.busProfit
		
	#更新最大／最小利润
	def updateBusMaxMinProfit (self):
		#更新单次完整交易最高盈利
		if self.busProfit > self.maxBusProfit:
			self.maxBusProfit = self.busProfit
			
		#更新单次完整交易最低盈利
		if self.busProfit < self.minBusProfit:
			self.minBusProfit = self.busProfit
			
'''
报单利润及回撤类
'''
class OrderRegress:
	def __init__ (self,
		debug = False,	#调试模式
		):
		self.debug = debug
		self.lock = thread.allocate_lock()	#保护锁，保护整个数据结构
		self.maxOrderWin = 0			#最大盈利单
		self.maxOrderLoss = 0			#最大止损单
		
	#打印调试信息
	def dbg (self,
		dbgInfo,	#debug信息
		):
		if self.debug:
			print '	OrderRegress: %s' % dbgInfo
			
	#更新最大报单赢利和亏损
	def updateOrderMaxWinLoss (self, 
		profit,	#利润
		):
		self.lock.acquire()
		
		if profit > self.maxOrderWin:
			self.maxOrderWin = profit
			
		if profit < self.maxOrderLoss:
			self.maxOrderLoss = profit
			
		self.lock.release()
		