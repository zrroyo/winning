#-*- coding:utf-8 -*-

import logging
import time
from futures import ApiStruct
import ctpapi
from elemmap import ElementMap

class MarketDataAgent:
	def __init__ (self):
		self.dataMap = ElementMap()
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
			
			if self.dataMap.isElementExisted(dp.InstrumentID):
				#已接受过该合约行情，如果行情发生改变则更新映射
				#print dp.Volume, self.dataMap.getMdData(dp.InstrumentID).Volume
				if dp.Volume <= self.dataMap.getElement(dp.InstrumentID).Volume:
					#行情未变化
					#self.logger.debug(u'MD:行情无变化，inst=%s,time=%s，volume=%s,last_volume=%s' % (dp.InstrumentID,dp.UpdateTime,dp.Volume,self.dataMap.getMdData(dp.InstrumentID).Volume))
					return 
			
				#行情发生变化，记录到行情数据映射中.
				self.dataMap.updateElement(dp.InstrumentID, dp)
			else:	
				#合约行情数据还不存在于已知映射中
				self.dataMap.addElement(dp.InstrumentID, dp)
	
			print u'[%s]，[价：最新/%d，买/%d，卖/%d], [量：买/%d，卖/%d，总：%d], [最高/%d，最低/%d], 时间：%s' % (dp.InstrumentID, dp.LastPrice, dp.BidPrice1, dp.AskPrice1, dp.BidVolume1, dp.AskVolume1, dp.Volume, dp.HighestPrice, dp.LowestPrice, dp.UpdateTime)
		finally:
			self.logger.debug(u'接收行情数据异常!')
			
		pass
		
		
class TraderAgent:
	def __init__ (self,
		instruments, 	#合约 
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
		#self.logger = logging.getLogger('ctp.agent.%s' % self.instruments)
		self.trader = None
		self.isSettlementInfoConfirmed = False  #结算单未确认
			
		self.broker_id = broker_id
		self.investor_id = investor_id
		self.passwd = passwd
		self.server_port = server_port
		
		self.orderMap = ElementMap()		#报单管理映射
		self.errOrderMap = ElementMap()		#错误报单映射
		
	#init中的init,用于子类的处理
	def init_init (self):
		#初始化日志管理
		logName = 'ctp_%s.log' % self.instruments
		logging.basicConfig(filename=logName,level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
		self.logger = logging.getLogger('ctp')
		
		#初始化CTP交易接口
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
		print u'FrondId %s, SessionID %s, OrderRef %s' % (frontID, sessionID, max_order_ref)
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
		
	def close_position (self, direction, price, volume, cos_flag=ApiStruct.OF_Close):
		self.trader.close_position(self.instruments, direction, self.inc_order_ref(), price, volume, cos_flag)
		
	#回调函数响应：CTP报单通知
	def rtn_order (self, order):
		#接收报单状态，并更新在报单映射中
		self.orderMap.addElement(order.OrderRef, order)
		
	#回调函数响应：CTP成交通知
	def rtn_trade (self, trader):
		#报单成交，从报单映射中删除
		self.orderMap.delElement(trader.OrderRef)
		
	#提出撤单申请
	def cancel_command(self, instrument, order_ref):
		order = str(order_ref)
		self.trader.cancel_command(instrument, order_ref)
		time.sleep(1)
		
		print self.errOrderMap.elemDict
		#错误报单映射中无记录证明成功撤单
		if self.errOrderMap.isElementExisted(order):
			#撤单失败，清除记录
			self.errOrderMap.delElement(order)
		else:
			#撤单成功，从报单映射中清除
			self.orderMap.delElement(order)
		 
	#def err_order_insert (self, ptrader):
		#pass
			
	#回调函数响应：CTP撤单错误通知
	def err_order_action (self, pInputOrderAction):
		self.errOrderMap.addElement(pInputOrderAction.OrderRef, pInputOrderAction)
			
	def query_order (self, instrument, order_sys_id):
		self.trader.query_order(instrument, order_sys_id)
		
	#回调函数响应：CTP报单查询
	def rsp_qry_order (self, order):
		print order
		pass	
		