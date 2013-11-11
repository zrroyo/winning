#-*- coding:utf-8 -*-

import logging
import time
from futures import ApiStruct
import ctpapi
import mdmap

class MarketDataAgent:
	def __init__ (self):
		self.dataMap = mdmap.MarketDataMap()
		pass
		
	# 在开始行情服务前必须被调用	
	def initAgent (self, logger, instList):
		self.logger = logger
		self.instruments = instList
		pass
		
	# CtpMdApi对象OnRtnDepthMarketData成员方法的真实回调函数	
	def OnRtnDepthMarketData (self, depth_market_data):
		#print "Agent:OnRtnDepthMarketData"
		dp = depth_market_data
		try:
			if dp.LastPrice > 999999 or dp.LastPrice < 10:
				self.logger.warning(u'MD:收到的行情数据有误:%s,LastPrice=:%s' %(dp.InstrumentID,dp.LastPrice))
			if dp.InstrumentID not in self.instruments:
				self.logger.warning(u'MD:收到未订阅的行情:%s' %(dp.InstrumentID,))
				return
			
			if self.dataMap.isMdDataExisted(dp.InstrumentID):
				#已接受过该合约行情，如果行情发生改变则更新映射
				#print dp.Volume, self.dataMap.getMdData(dp.InstrumentID).Volume
				if dp.Volume <= self.dataMap.getMdData(dp.InstrumentID).Volume:
					#行情未变化
					#self.logger.debug(u'MD:行情无变化，inst=%s,time=%s，volume=%s,last_volume=%s' % (dp.InstrumentID,dp.UpdateTime,dp.Volume,self.dataMap.getMdData(dp.InstrumentID).Volume))
					return 
			
				#行情发生变化，记录到行情数据映射中.
				self.dataMap.updateMdData(dp.InstrumentID, dp)
			else:	
				#合约行情数据还不存在于已知映射中
				self.dataMap.addMdData(dp.InstrumentID, dp)
	
			print u'[%s]，[价：最新/%d，买/%d，卖/%d], [量：买/%d，卖/%d，总：%d], [最高/%d，最低/%d], 时间：%s' % (dp.InstrumentID, dp.LastPrice, dp.BidPrice1, dp.AskPrice1, dp.BidVolume1, dp.AskVolume1, dp.Volume, dp.HighestPrice, dp.LowestPrice, dp.UpdateTime)
		finally:
			self.logger.debug(u'接收行情数据异常!')
			
		pass
		
		
class TraderAgent:
	def __init__ (self,
		instruments, 	#合约映射 name ==>c_instrument 
		broker_id,   	#期货公司ID
		investor_id, 	#投资者ID
		passwd,	 	#口令
		server_port	#交易服务器端口
		):
		'''
		trader为交易对象
		tday为当前日,为0则为当日
		'''
		self.instruments = instruments
		self.request_id = 1
		self.initialized = False
		self.front_id = None
		self.session_id = None
		self.order_ref = 1
		self.trading_day = 20110101
		self.scur_day = int(time.strftime('%Y%m%d'))
		self.logger = logging.getLogger('ctp.agent.%s' % self.instruments)
	
		self.broker_id = broker_id
		self.investor_id = investor_id
		self.passwd = passwd
		self.server_port = server_port
		self.trader = None
		
		print self.broker_id
		
		#结算单
		self.isSettlementInfoConfirmed = False  #结算单未确认
		
	#init中的init,用于子类的处理
	def init_init (self):
		traderSpi = ctpapi.CtpTraderApi(self.instruments, self.broker_id, self.investor_id, self.passwd, self)
		traderSpi.Create("TraderAgent")
		traderSpi.RegisterFront(self.server_port)
		traderSpi.Init()
		self.trader = traderSpi
		#self.initialized = True
		pass
		
	def initialize (self):
		while self.isSettlementInfoConfirmed == False:
			time.sleep(1)
		print u'代理初始化完成'
		pass
		
	def login_success (self,frontID, sessionID, max_order_ref):
		#print u'FrondId %s, SessionID %s, OrderRef %s' % (frontID, sessionID, max_order_ref)
		self.front_id = frontID
		self.session_id = sessionID
		self.order_ref = int(max_order_ref)
	
	def inc_request_id (self):
		self.request_id += 1
		return self.request_id
	
	def inc_order_ref(self):
		self.order_ref += 1
		return self.order_ref
		
	def open_position (self, direction, price, volume):
		self.trader.open_position(self.instruments, direction, self.inc_order_ref(), price, volume)
		
		pass
	
	def close_position (self, direction, price, volume, cos_flag=ApiStruct.OF_Close):
		self.trader.close_position(self.instruments, direction, self.inc_order_ref(), price, volume, cos_flag)
		
		pass
		
	def rtn_order (self, porder):
		pass
	
	def rtn_trade (self, ptrader):
		pass
		 
	#def err_order_insert (self, ptrader):
		#pass
			