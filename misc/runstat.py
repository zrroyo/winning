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
		self.tradeCounter = TradingCounter()	#交易数据记录接口
		
		#利润及回撤
		self.regress = ProfitRegress(debug = False, 
					numInstruments = numInstruments
					)
		
		#初始化交易赢利接口
		self.busWin = BusinessWin(debug = False)
		#初始化报单赢利接口
		self.orderWin = OrderWin(debug = True)
	
	#更新单次完整交易的利润
	def updateBusinessMaxMinWin (self, 
		profit,	#利润
		):
		#更新单次完整交易最高盈利
		if profit > self.busWin.maxBusinessWin:
			self.busWin.maxBusinessWin = profit
			
		#更新单次完整交易最低盈利
		if profit <  self.busWin.minBusinessWin:
			self.busWin.minBusinessWin = profit
			
	#累积报单利润
	def addProfit (self, 
		profit,	#利润
		):
		self.regress.addProfit(profit)
			
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
		
	#更新最大报单赢利和亏损
	def updateOrderMaxWinLoss (self, 
		profit,	#利润
		):
		self.orderWin.updateOrderMaxWinLoss(profit)
		
	#更新所有
	def update (self, 
		profit,	#利润
		):
		self.updateOrderMaxWinLoss(profit)
		self.updateMaxMinProfit(profit, None)
		self.addProfit(profit)
		
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
		self._formatPrint("      Max Order Win", self.orderWin.maxOrderWin)
		self._formatPrint("     Max Order Loss", self.orderWin.maxOrderLoss)
		self._formatPrint("   Max Business Win", self.busWin.maxBusinessWin)
		self._formatPrint("   Min Business Win", self.busWin.minBusinessWin)
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
		self.updateOrderMaxWinLoss(profit)
		self.addProfit(profit)
		self.lock.release()
	
	#更新单次完整交易的利润
	def updateBusinessMaxMinWin (self, 
		profit,	#利润
		):
		self.lock.acquire()
		if self.curPoses != 0:
			self.busWin.addBusWin(profit)
			self.lock.release()
			return
		'''
		当前持仓数为0表明一次完整交易结束，应进行统计。
		'''
		
		self.busWin.addBusWin(profit)
		self.busWin.updateBusinessMaxMinWin()
		
		#更新交易数据记录
		if self.busWin.getBusWin() > 0:
			self.tradeCounter.incNumBusWin()
		elif self.busWin.getBusWin() < 0:
			self.tradeCounter.incNumBusLoss()
		else:
			self.tradeCounter.incNumBusFlat()
			
		#单次交易完成，当前利润清0
		self.busWin.clearBusWin()
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
		self._formatPrint("      Max Order Win", self.orderWin.maxOrderWin)
		self._formatPrint("     Max Order Loss", self.orderWin.maxOrderLoss)
		self._formatPrint("   Max Business Win", self.busWin.maxBusinessWin)
		self._formatPrint("   Min Business Win", self.busWin.minBusinessWin)
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
	