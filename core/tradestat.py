#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2016年 10月 15日 星期六 18:16:17 CST

交易数据统计模块
"""

import core.emulation as emul

# Tick统计属性
TK_FLOAT_MOV 		= 'Float_Move'			#浮赢
TK_FLOAT_CUM 		= 'Float_Pro_Cum'		#累积浮赢
TK_FLOAT_POS 		= 'Float_Pro_Pos'		#持仓浮赢
TK_ORD_PROFIT 		= 'Order_Profit'		#平仓利润
TK_ADD_POS 		= 'Add_Pos'			#加仓
TK_CUT_LOSES 		= 'Cut_Loss'			#止损
TK_STOP_WINS 		= 'Stop_Win'			#止赢
TK_ORD_WINS 		= 'Order_Win'			#赢利单数
TK_ORD_LOSS 		= 'Order_Loss'			#亏损单数
TK_ORD_FLAT 		= 'Order_Flat'			#持平单数
TK_RES_POS 		= 'Res_Pos'			#仓位（tick恢复）
TK_RES_CAP 		= 'Res_Cap'			#资金（tick恢复）
TK_RES_ACT 		= 'Res_Act'			#操作类型（tick恢复）

# Tick统计表头
TICK_STATS = [TK_FLOAT_MOV, TK_FLOAT_CUM, TK_FLOAT_POS, TK_ORD_PROFIT, TK_ADD_POS, \
	      TK_CUT_LOSES, TK_STOP_WINS, TK_ORD_WINS, TK_ORD_LOSS, TK_ORD_FLAT, \
	      TK_RES_POS, TK_RES_CAP, TK_RES_ACT]

class TickStat:
	def __init__ (self):
		"""
		Tick统计记录
		"""
		self.floatProfit = 0.0
		self.floatProPos = 0.0
		self.floatProCum = 0.0
		self.orderProfit = 0.0	#平仓利润
		self.addPos = 0
		self.cutLoss = 0
		self.stopWin = 0
		self.ordWins = 0	#赢利单数
		self.ordLoses = 0	#亏损单数
		self.ordFlat = 0	#持平单数
		self.resPos = 0
		self.resCap = 0.0
		self.resAct = emul.MEUL_FUT_ACT_SKIP
		self.tagTradeEnd = False	#交易结束标志
		self.reqtype = 0	#sched req类型

	def values (self):
		"""
		生成tick数据插入记录
		:return: 统计数据列表
		"""
		return [self.floatProfit, self.floatProCum, self.floatProPos, \
			self.orderProfit, self.addPos, self.cutLoss, self.stopWin, \
			self.ordWins, self.ordLoses, self.ordFlat, \
			self.resPos, self.resCap, self.resAct]

# 交易统计属性
TRD_TICK_START		= 'Tick_Start'			#开始Tick
TRD_TICK_END		= 'Tick_End'			#结束Tick
TRD_DAYS_LAST		= 'Days_Last'			#持续天数
TRD_ADD_POS 		= TK_ADD_POS			#总加仓数
TRD_CUT_LOSES 		= TK_CUT_LOSES			#总止损数
TRD_STOP_WINS 		= TK_STOP_WINS			#总止赢数
TRD_ORD_WINS 		= TK_ORD_WINS			#总赢利单数
TRD_ORD_LOSS		= TK_ORD_LOSS			#总亏损单数
TRD_ORD_FLAT		= TK_ORD_FLAT			#总持平单数
TRD_TICK_FLOAT_MAX	= 'Tick_Float_Max'		#浮赢最高Tick
TRD_TICK_FLOAT_MIN	= 'Tick_Float_Min'		#浮赢最低Tick
TRD_FLOAT_MEAN		= 'Float_Mean'			#浮羸均值
TRD_FLOAT_STD		= 'Float_Std'			#浮赢标准差
TRD_FLOAT_MIN		= 'Float_Min'			#浮赢最低值
TRD_FLOAT_25		= 'Float_0.25'			#浮赢0.25分位
TRD_FLOAT_50		= 'Float_0.50'			#浮赢0.50分位
TRD_FLOAT_75		= 'Float_0.75'			#浮赢0.75分位
TRD_FLOAT_MAX		= 'Float_Max'			#浮赢最高值
TRD_PROFIT		= 'Profit'			#利润

# 交易统计表头
TRADE_STATS = [TRD_TICK_START, TRD_TICK_END, TRD_DAYS_LAST, TRD_ADD_POS, \
	       TRD_CUT_LOSES, TRD_STOP_WINS, TRD_ORD_WINS, TRD_ORD_LOSS, TRD_ORD_FLAT, \
	       TRD_TICK_FLOAT_MAX, TRD_TICK_FLOAT_MIN, TRD_FLOAT_MEAN, TRD_FLOAT_STD, \
	       TRD_FLOAT_MIN, TRD_FLOAT_25, TRD_FLOAT_50, TRD_FLOAT_75, TRD_FLOAT_MAX, TRD_PROFIT]

class TradeStat:
	def __init__ (self):
		"""
		交易统计记录(交易始于仓数由0变1，止于仓数由>=1变为0)
		"""
		self.tickStart = None
		self.tickEnd = None
		self.profit = 0
		self.daysLast = 0
		self.tickFloatMax = None
		self.tickFloatMin = None
		self.cumFloat = 0.0

	def values (self, sumBuf, descBuf):
		"""
		生成交易数据，按插入次序排列
		:param sumBuf: sum(交易表)汇总数据
		:param descBuf: 交易表.describe()数据
		:return: 统计数据列表
		"""
		return [self.tickStart, self.tickEnd, self.daysLast, \
			sumBuf[TRD_ADD_POS], sumBuf[TRD_CUT_LOSES], sumBuf[TRD_STOP_WINS], \
			sumBuf[TRD_ORD_WINS], sumBuf[TRD_ORD_LOSS], sumBuf[TRD_ORD_FLAT], \
			self.tickFloatMax, self.tickFloatMin, descBuf['mean'], descBuf['std'], \
			descBuf['min'], descBuf['25%'], descBuf['50%'], descBuf['75%'], descBuf['max'], \
			self.profit]

class CommonStat:
	def __init__ (self):
		"""
		通用统计属性，定义会被用到但非专用统计属性
		"""
		self.cumProfit = 0.0
