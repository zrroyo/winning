#-*- coding:utf-8 -*-

'''
运行时统计信息模块(Run-time Statistics Module)
	-- 统计各种运行时感兴趣的信息。
'''

import thread
from profit import *
from tradecounter import *

'''
运行时统计类(Run-time Statistics Class)
	-- 只适用于单合约统计
'''
class RunStat:
	def __init__ (self, 
		name=None,
		numInstruments = 1,	#并行执行的合约数量
		):
		self.name = name	#合约
		self.maxOrderWin = 0	#最大盈利单
		self.maxOrderLoss = 0	#最大止损单
		self.tradeCounter = TradingCounter()	#交易数据记录接口
		
		#利润及回撤
		self.regress = ProfitRegress(debug = False, 
					numInstruments = numInstruments
					)
		
		#初始化完整交易利润及回撤接口
		self.busRegress = BusinessProfitRegress(debug = False)
		
	#更新最大盈利单
	def updateOrderMaxWin (self, 
		profit,	#利润
		):
		if profit > self.maxOrderWin:
			self.maxOrderWin = profit
	
	#更新最大止损单
	def updateOrderMaxLoss (self, 
		profit,	#利润
		):
		if profit < self.maxOrderLoss:
			self.maxOrderLoss = profit
			
	#更新单次完整交易的利润
	def updateBusinessProfit (self, 
		profit,	#利润
		):
		#更新单次完整交易最高盈利
		if profit > self.busRegress.maxBusProfit:
			self.busRegress.maxBusProfit = profit
			
		#更新单次完整交易最低盈利
		if profit <  self.busRegress.minBusProfit:
			self.busRegress.minBusProfit = profit
			
	#更新利润(以交易单为单位)
	def updateProfitByOrder (self, 
		profit,	#利润
		):
		self.regress.updateProfitByOrder(profit)
			
		#更新交易数据记录
		if profit > 0:
			self.tradeCounter.incNumOrderWin()
		elif profit < 0:
			self.tradeCounter.incNumOrderLoss()
		else:
			self.tradeCounter.incNumOrderFlat()
			
	#更新最大最小利润
	def updateMaxMinProfit (self, 
		profit,	#利润
		time,	#交易日
		):
		self.regress.updateMaxMinProfit(profit, time)
		
	#更新所有
	def update (self, 
		profit,	#利润
		):
		self.updateOrderMaxWin(profit)
		self.updateOrderMaxLoss(profit)
		self.updateMaxMinProfit(profit, None)
		self.updateProfitByOrder(profit)
		
	#固定格式输出
	def _formatPrint (self, 
		comment,	#输出内容
		value,		#输出值
		):
		print "		  %s:	%s" % (comment, value)
		
	#显示统计
	def showStat (self):
		print "\n		* * * * * * * * * * * * * "
		print "		Show Run Time Statistics for [ %s ]:" % self.name
		self._formatPrint("      Max Order Win", self.maxOrderWin)
		self._formatPrint("     Max Order Loss", self.maxOrderLoss)
		self._formatPrint("Max Business Profit", self.busRegress.maxBusProfit)
		self._formatPrint("Min Business Profit", self.busRegress.minBusProfit)
		self._formatPrint("         Max Profit", self.regress.maxProfit)
		self._formatPrint("         Min Profit", self.regress.minProfit)
		self._formatPrint("       Total Profit", self.regress.profit)
		print "		* * * * * * * * * * * * * \n"
	
'''
市场运行时统计类(Market Run-time Statistics Class)
	-- 运行时对整个市场中的多个合约并行统计。
'''
class MarketRunStat(RunStat):
	def __init__ (self, 
		maxAllowedPos,	#最大允许的仓位(单位)
		mute=False	#是否输出统计信息
		):
		RunStat.__init__(self,
				name=None,
				numInstruments = 2,
				)
		self.curFutCode = None			#当前合约
		self.maxAllowedPos = maxAllowedPos	#最大允许的持仓数(加仓次数)
		self.curPoses = 0			#当前对整个市场的持仓数（加仓次数）
		self.lock = thread.allocate_lock()	#运行时保护锁，保护整个数据结构
		self.mute = mute
		
	#开仓
	def openPosition (self):
		'''
		如果仓位已满返回False表示不允许开仓，反之返回True，并且仓位加1。
		'''
		self.lock.acquire()
		if self.curPoses >= self.maxAllowedPos:
			self.lock.release()
			return False
		
		#增加开仓数
		self.tradeCounter.incNumOpen()
		#初次开仓，增加交易数
		if self.curPoses == 0:
			self.tradeCounter.incNumTrade()
			
		self.curPoses += 1
		self.lock.release()
		return True	
	
	#平仓
	def closePosition (self, 
		poses,	#所平仓数目
		):
		'''
		正常情况仓位减1，返回True。
		'''
		self.lock.acquire()
		if self.curPoses <= 0 or self.curPoses < poses:
			self.lock.release()
			print u'MarketRunStat: closePosition error'
			return False
		
		#增加平仓数
		self.tradeCounter.incNumClose()
		
		self.curPoses -= poses
		self.lock.release()
		return True
	
	#市场是否已经满仓
	def fullPositions (self):
		retVal = False
		self.lock.acquire()
		if self.curPoses >= self.maxAllowedPos:
			retVal = True
		
		self.lock.release()
		return retVal
	
	#更新所有
	def update (self, 
		profit,	#利润
		):
		self.lock.acquire()
		#RunStat.update(self, profit)
		self.updateOrderMaxWin(profit)
		self.updateOrderMaxLoss(profit)
		self.updateProfitByOrder(profit)
		self.lock.release()
	
	#更新单次完整交易的利润
	def updateBusinessProfit (self, 
		profit,	#利润
		):
		self.lock.acquire()
		if self.curPoses != 0:
			self.busRegress.addProfit(profit)
			self.lock.release()
			return
		'''
		当前持仓数为0表明一次完整交易结束，应进行统计。
		'''
		
		self.busRegress.addProfit(profit)
		self.busRegress.updateBusMaxMinProfit()
		
		#更新交易数据记录
		if self.busRegress.getBusProfit() > 0:
			self.tradeCounter.incNumBusWin()
		elif self.busRegress.getBusProfit() < 0:
			self.tradeCounter.incNumBusLoss()
		else:
			self.tradeCounter.incNumBusFlat()
			
		#单次交易完成，当前利润清0
		self.busRegress.clearProfit()
		self.lock.release()
			
	#固定格式输出
	def _formatPrint (self, 
		comment,	#输出内容
		value		#输出值
		):
		print "	  %s:	%s" % (comment, value)
		
	#显示统计
	def showMarRunStat (self):
		if self.mute == True:
			return
		
		self.lock.acquire()
		if self.curPoses != 0:
			self.lock.release()
			return
		
		print "\n	* * * * * * * * * * * * * "
		print "	Market Run Time Statistics:"
		self._formatPrint("      Max Order Win", self.maxOrderWin)
		self._formatPrint("     Max Order Loss", self.maxOrderLoss)
		self._formatPrint("Max Business Profit", self.busRegress.maxBusProfit)
		self._formatPrint("Min Business Profit", self.busRegress.minBusProfit)
		self._formatPrint("         Max Profit", self.regress.maxProfit)
		self._formatPrint("         Min Profit", self.regress.minProfit)
		self._formatPrint("       Total Profit", self.regress.profit)
		#self._formatPrint("  Current Positions", self.curPoses)
		print "\n	Trading Counters:"
		self._formatPrint("       Open Numbers", self.tradeCounter.numOpen)
		self._formatPrint("      Close Numbers", self.tradeCounter.numClose)
		self._formatPrint("          Order Win", self.tradeCounter.numOrderWin)
		self._formatPrint("         Order Loss", self.tradeCounter.numOrderLoss)
		self._formatPrint("         Order Flat", self.tradeCounter.numOrderFlat)
		self._formatPrint("     Order Win Rate", self.tradeCounter.orderWinRate())
		self._formatPrint("       Business Win", self.tradeCounter.numBusWin)
		self._formatPrint("      Business Loss", self.tradeCounter.numBusLoss)
		self._formatPrint("      Business Flat", self.tradeCounter.numBusFlat)
		self._formatPrint("      Trade Numbers", self.tradeCounter.numTrade)
		self._formatPrint("  Business Win Rate", self.tradeCounter.busWinRate())
		print "	* * * * * * * * * * * * * \n"
		
		self.lock.release()
	