#-*- coding:utf-8 -*-

'''
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2015年 05月 31日 星期日 16:24:26 CST

数据统计模块
'''

import sys
sys.path.append("..")

from misc.debug import *
from db.sql import *
from db.tbldesc import *

#默认存储统计信息的数据库
DEF_DUMP_DATABASE = 'windump'

#默认tick值
DEF_TICK = '0000-00-00'

#合约利润
class ProfitStat:
	
	final = 0		#最终利润
	maxFloating = 0		#最高浮动利润
	minFloating = 0		#最低浮动利润
	maxFloatTick = DEF_TICK	#最高浮动利润出现Tick
	minFloatTick = DEF_TICK	#最低浮动利润出现Tick
	sum = 0			#累积利润
	maxSum = 0		#最高累积利润
	minSum = 0		#最大累积亏损
	maxSumTick = DEF_TICK	#最高累积利润出现Tic
	minSumTick = DEF_TICK	#最大累积亏损出现Tick
	
	def __init__ (self,
		contract,		#合约名
		dumpName = None,	#统计信息Dump名
		debug = False,		#调试模式
		):
		self.debug = Debug('ProfitStat', debug)	#调试接口
		self.dumpName = dumpName
		self.contract = contract
		self.startTick = None
		
		#初始化Dump接口
		if dumpName:
			self.__initDump()
	
	#初始化Dump接口
	def __initDump (self):
		#初始化数据库连接
		self.db = SQL()
		self.db.connect(DEF_DUMP_DATABASE)
		
		#如果数据表已存大，则不再创建
		self.dumpTable = "%s_profit" % self.dumpName
		if self.db.ifTableExist(self.dumpTable):
			return
		
		#创建存储数据表
		strSql = '''create table %s (
				%s int(4) not null primary key auto_increment,
				%s varchar(10),
				%s datetime default 0,
				%s datetime default 0,
				%s float default 0.0,
				%s datetime default 0,
				%s float default 0.0,
				%s datetime default 0,
				%s float default 0.0)''' % (self.dumpTable, PSD_F_ID,
						PSD_F_CONTRACT, PSD_F_TICK_START, PSD_F_TICK_END, 
						PSD_F_MAX, PSD_F_MAX_TICK, PSD_F_MIN, PSD_F_MIN_TICK,
						PSD_F_FINAL)
		
		self.debug.dbg("__initDump: %s" % strSql)
		self.db.execSql(strSql)
	
	#开始交易利润统计
	def start (self,
		tick,	#时间
		):
		#记录第一个tick以备后续关键字匹配更新数据库
		self.startTick = tick
		#插入一条新记录
		values = "0, '%s', '%s', Null, Null, Null, Null, Null, Null" % (self.contract, tick)
		self.db.insert(self.dumpTable, values)
	
	#结束交易利润统计
	def end (self,
		tick,	#时间
		):
		'''
		一次交易结束，将各统计信息更新到数据库。
		'''
		values = "%s = '%s', %s = '%s', %s = '%s', %s = '%s', %s = '%s', %s = '%s'" % (
			PSD_F_TICK_END, tick, 
			PSD_F_MAX, self.maxFloating,
			PSD_F_MAX_TICK, self.maxFloatTick,
			PSD_F_MIN, self.minFloating,
			PSD_F_MIN_TICK, self.minFloatTick,
			PSD_F_FINAL, self.final)
			
		self.debug.dbg("end: %s" % values)
		
		clause = "%s = '%s' and %s = '%s'" % (
			PSD_F_TICK_START, self.startTick, 
			PSD_F_CONTRACT, self.contract)
			
		self.db.update(self.dumpTable, clause, values)
		
		#交易结束将只跟本次交易相关的统计信息重置清零
		self.final = self.maxFloating = self.minFloating = 0
		self.maxFloatTick = self.minFloatTick = DEF_TICK
	
	#利润增加
	def add (self,
		tick,	#时间
		profit,	#利润
		):
		#累加最终利润、累积利润
		self.final += profit
		self.sum += profit
	
	#巡航。在交易时间中即使没有交易发生，只要有持仓相关数据就会发生波动。
	def navigate (self,
		tick,	#时间
		profit,	#利润
		):
		#更新累积利润最大、最小值
		sum = self.sum + profit
		if sum > self.maxSum:
			self.maxSum = sum
			self.maxSumTick = tick
		elif sum < self.minSum:
			self.minSum = sum
			self.minSumTick = tick
		
		#更新当前Trade利润最大、最小值
		final = self.final + profit
		if final > self.maxFloating:
			self.maxFloating = final
			self.maxFloatTick = tick
		elif final < self.minFloating:
			self.minFloating = final
			self.minFloatTick = tick
			
		self.debug.dbg("navigate %s: sum %s max %s min %s, final %s, max %s min %s" % (
			tick, sum, self.maxSum, self.minSum, final, self.maxFloating, self.minFloating))
	
	#得到最终利润
	def getFinal (self):
		return self.final
	
	#得到累积利润
	def getSum (self):
		return self.sum
	
#下单统计
class OrderStat:
	
	nWins = 0		#赢利单数
	nLoses = 0		#亏损单数
	nFlat = 0		#持平单数
	maxOrderWin = 0		#最大单赢利
	maxOrderLoss = 0	#最大单亏损
	
	def __init__ (self,
		contract,		#合约名
		dumpName = None,	#统计信息Dump名
		debug = False,		#调试模式
		):
		self.debug = Debug('OrderStat', debug)	#调试接口
		self.contract = contract
		self.dumpName = dumpName

		#初始化Dump接口
		if dumpName:
			self.__initDump()
	
	#初始化Dump接口
	def __initDump (self):
		#初始化数据库连接
		self.db = SQL()
		self.db.connect(DEF_DUMP_DATABASE)
		
		#如果数据表已存大，则不再创建
		self.dumpTable = "%s_order" % self.dumpName
		if self.db.ifTableExist(self.dumpTable):
			return
		
		#创建存储数据表
		strSql = '''create table %s (
				%s int(4) not null primary key auto_increment,
				%s varchar(10),
				%s datetime default 0,
				%s float default 0.0,
				%s datetime default 0,
				%s float default 0.0,
				%s int(1),
				%s int(4) default 0,
				%s float default 0)''' % (self.dumpTable, 
						OSD_F_ID, OSD_F_CONTRACT, OSD_F_TICK_OPEN, 
						OSD_F_OPEN, OSD_F_TICK_CLOSE, OSD_F_CLOSE, 
						OSD_F_DIRECTION, OSD_F_VOLUME, OSD_F_PROFIT)
		
		self.debug.dbg("__initDump: %s" % strSql)
		self.db.execSql(strSql)
	
	#记录统计信息
	def dumpStat (self,
		tick,		#时间
		price,		#价格
		position,	#仓位信息
		orderProfit,	#平仓利润
		):
		#将数据插入数据库
		values = "0, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'" % (
				self.contract, position.time, position.price, tick, 
				price, position.direction, position.volume, orderProfit)

		self.db.insert(self.dumpTable, values)
	
	#计算
	def add (self,
		tick,		#时间
		price,		#价格
		position,	#仓位信息
		orderProfit,	#平仓利润
		):
		#更新下单统计
		if orderProfit > 0:
			self.nWins += 1
		elif orderProfit < 0:
			self.nLoses += 1
		else:
			self.nFlat += 1
			
		#更新最大单赢利
		if orderProfit > self.maxOrderWin:
			self.maxOrderWin = orderProfit
			
		#更新最大单亏损
		if orderProfit < self.maxOrderLoss:
			self.maxOrderLoss = orderProfit
			
		#存储交易单
		if self.dumpName:
			self.dumpStat(tick, price, position, orderProfit)
	
	#总单数
	def numOrders (self):
		return self.nWins + self.nLoses + self.nFlat
	
#合约统计
class ContractStat:
	def __init__ (self,
		contract,		#合约名
		dumpName = None,	#统计信息Dump名
		debug = False,		#是否调试
		):
		self.contract = contract
		self.debug = Debug('ContractStat', debug)	#调试接口
		self.profit = ProfitStat(contract, dumpName, debug)	#
		self.order = OrderStat(contract, dumpName, debug)	#
	
	#开始合约统计
	def start (self,
		tick,	#时间
		):
		#开始利润统计
		self.profit.start(tick)
	
	#结束合约统计
	def end (self,
		tick,	#时间
		):
		#结束利润统计
		self.profit.end(tick)
	
	#更新统计接口
	def update (self,
		tick,		#时间
		price,		#价格
		position,	#仓位信息
		orderProfit,	#利润
		):
		#进行统计
		self.profit.add(tick, orderProfit)
		self.order.add(tick, price, position, orderProfit)
	
	#巡航
	def navigate (self,
		tick,	#时间
		profit,	#利润
		):
		#利润统计巡航
		self.profit.navigate(tick, profit)
	
	#固定格式输出
	def __formatPrint (self, 
		comment,	#输出内容
		value,		#输出值
		):
		print "		  %s:	%s" % (comment, value)
	
	#显示统计
	def show (self):
		print "\n		* * * * * * * * * * * * * "
		print "		Show Run Time Statistics for [ %s ]:" % self.contract
		self.__formatPrint("         Order Wins", self.order.nWins)
		self.__formatPrint("        Order Loses", self.order.nLoses)
		self.__formatPrint("        Order Total", self.order.numOrders())
		self.__formatPrint("      Max Order Win", self.order.maxOrderWin)
		self.__formatPrint("     Max Order Loss", self.order.maxOrderLoss)
		self.__formatPrint("   Max Business Win", self.profit.maxFloating)
		self.__formatPrint("   Min Business Win", self.profit.minFloating)
		self.__formatPrint("         Max Profit", self.profit.maxSum)
		self.__formatPrint("         Min Profit", self.profit.minSum)
		self.__formatPrint("       Total Profit", self.profit.sum)
		print "		* * * * * * * * * * * * * \n"
		