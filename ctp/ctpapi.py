#-*- coding:utf-8 -*-

import logging
from futures import ApiStruct, MdApi, TraderApi
import ctpagent

# CTP行情数据接口
class CtpMdApi(MdApi):
	logger = logging.getLogger('ctp.CtpMdApi')
	
	def __init__(self, instruments, broker_id, investor_id, passwd, agent=None):
		self.requestid=0
		self.instruments = instruments
		self.broker_id =broker_id
		self.investor_id = investor_id
		self.passwd = passwd
		
		#初始化实际处理对象
		self.agent = agent
		if self.agent is not None:
			self.agent.initAgent(self.logger, self.instruments)
	
	def checkErrorRspInfo(self, info):
		if info.ErrorID !=0:
			logger.error(u"MD:ErrorID:%s,ErrorMsg:%s" %(info.ErrorID,info.ErrorMsg))
		return info.ErrorID !=0
	
	def OnRspError(self, info, RequestId, IsLast):
		self.logger.error(u'MD:requestID:%s,IsLast:%s,info:%s' % (RequestId,IsLast,str(info)))
	
	def OnFrontDisConnected(self, reason):
		self.logger.info(u'MD:front disconnected,reason:%s' % (reason,))
	
	def OnFrontConnected(self):
		self.logger.info(u'MD:front connected')
		self.user_login(self.broker_id, self.investor_id, self.passwd)
	
	def user_login(self, broker_id, investor_id, passwd):
		req = ApiStruct.ReqUserLogin(BrokerID=broker_id, UserID=investor_id, Password=passwd)
		self.requestid += 1
		r=self.ReqUserLogin(req, self.requestid)
	
	def OnRspUserLogin(self, userlogin, info, rid, is_last):
		print "OnRspUserLogin", is_last, info
		if is_last and not self.checkErrorRspInfo(info):
			print "get today's trading day:", repr(self.GetTradingDay())
			self.subscribe_market_data(self.instruments)
	
	def subscribe_market_data(self, instruments):
		self.SubscribeMarketData(list(instruments))
	
	def OnRtnDepthMarketData(self, depth_market_data):
		if self.agent is None:
			dp = depth_market_data
			print u'[%s]，[价：最新/%d，买/%d，卖/%d], [量：买/%d，卖/%d，总：%d], [最高/%d，最低/%d], 时间：%s' % (dp.InstrumentID, dp.LastPrice, dp.BidPrice1, dp.AskPrice1, dp.BidVolume1, dp.AskVolume1, dp.Volume, dp.HighestPrice, dp.LowestPrice, dp.UpdateTime)
		else:
			self.agent.OnRtnDepthMarketData(depth_market_data)
			
# CTP交易接口
class CtpTraderApi(TraderApi):
	logger = logging.getLogger('ctp.CtpTraderApi')
	
	def __init__(self,
		instruments, 	#合约映射 name ==>c_instrument 
		broker_id,   	#期货公司ID
		investor_id, 	#投资者ID
		passwd, 	#口令
		agent = None  	#实际操作对象
		):        
		self.instruments = instruments
		self.broker_id =broker_id
		self.investor_id = investor_id
		self.passwd = passwd
		self.agent = agent
		self.is_logged = False
		self.request_id = 0
	
	def isRspSuccess(self, RspInfo):
		return RspInfo == None or RspInfo.ErrorID == 0
	
	def login(self):
		self.logger.info(u'try login...')
		self.user_login(self.broker_id, self.investor_id, self.passwd)
	
	##交易初始化
	def OnFrontConnected(self):
		'''
		当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
		'''
		self.logger.info(u'TD:trader front connected')
		self.login()
	
	def OnFrontDisconnected(self, nReason):
		self.logger.info(u'TD:trader front disconnected,reason=%s' % (nReason,))
	
	def user_login(self, broker_id, investor_id, passwd):
		req = ApiStruct.ReqUserLogin(BrokerID=broker_id, UserID=investor_id, Password=passwd)
		#r=self.ReqUserLogin(req,self.agent.inc_request_id())
		r=self.ReqUserLogin(req, self.request_id)
	
	def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
		self.logger.info(u'TD:trader login')
		self.logger.debug(u"TD:loggin %s" % str(pRspInfo))
		if not self.isRspSuccess(pRspInfo):
			self.logger.warning('TD:trader login failed, errMsg=%s' %(pRspInfo.ErrorMsg))
			print u'综合交易平台登陆失败，请检查网络或用户名/口令'
			self.is_logged = False
			return
		
		self.is_logged = True
		self.logger.info(u'TD:trader login success')
		#self.agent.login_success(pRspUserLogin.FrontID,pRspUserLogin.SessionID,pRspUserLogin.MaxOrderRef)
		#self.settlementInfoConfirm()
		#self.agent.set_trading_day(self.GetTradingDay())
		#self.query_settlement_info()
		#self.query_settlement_confirm() 
	
	def OnRspUserLogout(self, pUserLogout, pRspInfo, nRequestID, bIsLast):
		'''登出请求响应'''
		self.logger.info(u'TD:trader logout')
		self.is_logged = False
		