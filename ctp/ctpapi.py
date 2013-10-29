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
			