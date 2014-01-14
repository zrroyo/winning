#-*- coding:utf-8 -*-

'''
运行时统计信息模块(Run-time Statistics Module)
	-- 统计各种运行时感兴趣的信息。
'''

import thread

'''
运行时统计类(Run-time Statistics Class)
	-- 只适用于单合约统计
'''
class RunStat:
	def __init__ (self, name=None):
		self.name = name	#合约
		self.maxOrderWin = 0	#最大盈利单
		self.maxOrderLoss = 0	#最大止损单
		self.maxProfit = 0	#盈利最高点
		self.minProfit = 0	#盈利最低点
		self.maxBusProfit = 0	#单次完整交易最高盈利
		self.minBusProfit = 0	#单次完整交易最低盈利
		self.profit = 0		#当前利润
		self.tradeCounter = TradingCounter()	#交易数据记录接口
		return
	
	def __exit__ (self):
		return
		
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
		if profit > self.maxBusProfit:
			self.maxBusProfit = profit
			
		#更新单次完整交易最低盈利
		if profit <  self.minBusProfit:
			self.minBusProfit = profit
			
	#更新利润
	def updateProfit (self, 
		profit,	#利润
		):
		#更新当前利润
		self.profit += profit
			
		#更新盈利最高点
		if self.profit > self.maxProfit:
			self.maxProfit = self.profit
			
		#更新盈利最低点
		if self.profit < self.minProfit:
			self.minProfit = self.profit
			
		#更新交易数据记录
		if profit > 0:
			self.tradeCounter.incNumOrderWin()
		elif profit < 0:
			self.tradeCounter.incNumOrderLoss()
		else:
			self.tradeCounter.incNumOrderFlat()
			
	#更新所有
	def update (self, 
		profit,	#利润
		):
		self.updateOrderMaxWin(profit)
		self.updateOrderMaxLoss(profit)
		self.updateProfit(profit)
		
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
		self._formatPrint("Max Business Profit", self.maxBusProfit)
		self._formatPrint("Min Business Profit", self.minBusProfit)
		self._formatPrint("         Max Profit", self.maxProfit)
		self._formatPrint("         Min Profit", self.minProfit)
		self._formatPrint("       Total Profit", self.profit)
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
		RunStat.__init__(self)
		self.curFutCode = None			#当前合约
		self.maxAllowedPos = maxAllowedPos	#最大允许的持仓数(加仓次数)
		self.curPoses = 0			#当前对整个市场的持仓数（加仓次数）
		self.lock = thread.allocate_lock()	#运行时保护锁
		self.busProfit = 0			#当前交易的利润
		self.mute = mute
		return
	
	def __exit__ (self):
		return
	
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
		RunStat.update(self, profit)
		self.lock.release()
	
	#更新单次完整交易的利润
	def updateBusinessProfit (self, 
		profit,	#利润
		):
		self.lock.acquire()
		if self.curPoses != 0:
			self.busProfit += profit
			self.lock.release()
			return
		'''
		当前持仓数为0表明一次完整交易结束，应进行统计。
		'''
		
		self.busProfit += profit
		
		#更新单次完整交易最高盈利
		if self.busProfit > self.maxBusProfit:
			self.maxBusProfit = self.busProfit
			
		#更新单次完整交易最低盈利
		if self.busProfit < self.minBusProfit:
			self.minBusProfit = self.busProfit
			
		#更新交易数据记录
		if self.busProfit > 0:
			self.tradeCounter.incNumBusWin()
		elif self.busProfit < 0:
			self.tradeCounter.incNumBusLoss()
		else:
			self.tradeCounter.incNumBusFlat()
			
		#单次交易完成，当前利润清0
		self.busProfit = 0
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
		self._formatPrint("Max Business Profit", self.maxBusProfit)
		self._formatPrint("Min Business Profit", self.minBusProfit)
		self._formatPrint("         Max Profit", self.maxProfit)
		self._formatPrint("         Min Profit", self.minProfit)
		self._formatPrint("       Total Profit", self.profit)
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
	