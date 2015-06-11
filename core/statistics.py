#! /usr/bin/python
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

#合约利润
class ProfitStat:
	
	current = 0	#当前利润
	sum = 0		#合约累积利润
	maxCurrent = 0	#当前Trade最高利润
	minCurrent = 0	#当前Trade最高亏损
	maxSum = 0	#最高累积利润
	minSum = 0	#最大累积亏损
	
	def __init__ (self,
		debug = False,	#调试模式
		):
		self.debug = Debug('ProfitStat', debug)	#调试接口
	
	#利润增加
	def add (self,
		profit,	#利润
		):
		#积加当前Trade利润、累积利润
		self.current += profit
		self.sum += profit
		
		#更新累积利润最大、最小值
		if self.sum > self.maxSum:
			self.maxSum = self.sum
		elif self.sum < self.minSum:
			self.minSum = self.sum
		
		#更新当前Trade利润最大、最小值
		if self.current > self.maxCurrent:
			self.maxCurrent = self.current
		elif self.current < self.minCurrent:
			self.minCurrent = self.current
	
	#重置利润
	def reset (self):
		#累积利润不更新
		self.current = 0
	
	#返回当前利润
	def getCurrent (self):
		return self.current
	
	#返回累积利润
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
	def counts (self,
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
		self.profit = ProfitStat(debug)	#
		self.order = OrderStat(contract, dumpName, debug)	#
	
	#更新统计接口
	def update(self,
		tick,		#时间
		price,		#价格
		position,	#仓位信息
		orderProfit,	#利润
		):
		#进行统计
		self.profit.add(orderProfit)
		self.order.counts(tick, price, position, orderProfit)
	
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
		self.__formatPrint("   Max Business Win", self.profit.maxCurrent)
		self.__formatPrint("   Min Business Win", self.profit.minCurrent)
		self.__formatPrint("         Max Profit", self.profit.maxSum)
		self.__formatPrint("         Min Profit", self.profit.minSum)
		self.__formatPrint("       Total Profit", self.profit.sum)
		print "		* * * * * * * * * * * * * \n"
		