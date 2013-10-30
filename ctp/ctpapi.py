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
		self.query_settlement_confirm()
	
	def OnRspUserLogout(self, pUserLogout, pRspInfo, nRequestID, bIsLast):
		'''登出请求响应'''
		self.logger.info(u'TD:trader logout')
		self.is_logged = False
		
	def resp_common(self,rsp_info,bIsLast,name='默认'):
		#self.logger.debug("resp: %s" % str(rsp_info))
		if not self.isRspSuccess(rsp_info):
			self.logger.info(u"TD:%s失败" % name)
			return -1
		elif bIsLast and self.isRspSuccess(rsp_info):
			self.logger.info(u"TD:%s成功" % name)
			return 1
		else:
			self.logger.info(u"TD:%s结果: 等待数据接收完全..." % name)
			return 0
			
	# 结算信息（查询）函数
	def query_settlement_confirm(self):
		'''
		这个基本没用，不如直接确认
		而且需要进一步明确：有史以来第一次确认前查询确认情况还是每天第一次确认查询情况时，返回的响应中
			pSettlementInfoConfirm为空指针. 如果是后者,则建议每日不查询确认情况,或者在generate_struct中对
			CThostFtdcSettlementInfoConfirmField的new_函数进行特殊处理
		CTP写代码的这帮家伙素质太差了，边界条件也不测试，后置断言也不整，空指针乱飞
		2011-3-1 确认每天未确认前查询确认情况时,返回的响应中pSettlementInfoConfirm为空指针
		并且妥善处理空指针之后,仍然有问题,在其中查询结算单无动静
		'''
		req = ApiStruct.QrySettlementInfoConfirm(BrokerID=self.broker_id,InvestorID=self.investor_id)
		self.ReqQrySettlementInfoConfirm(req,self.agent.inc_request_id())
		
	def query_settlement_info(self):
		#不填日期表示取上一天结算单,并在响应函数中确认
		self.logger.info(u'TD:取上一日结算单信息并确认,BrokerID=%s,investorID=%s' % (self.broker_id,self.investor_id))
		req = ApiStruct.QrySettlementInfo(BrokerID=self.broker_id,InvestorID=self.investor_id,TradingDay=u'')
		#print req.BrokerID,req.InvestorID,req.TradingDay
		time.sleep(1)
		self.ReqQrySettlementInfo(req,self.agent.inc_request_id())
	
	def confirm_settlement_info(self):
		self.logger.info(u'TD-CSI:准备确认结算单')
		req = ApiStruct.SettlementInfoConfirm(BrokerID=self.broker_id,InvestorID=self.investor_id)
		self.ReqSettlementInfoConfirm(req,self.agent.inc_request_id())
	
	def OnRspQrySettlementInfo(self, pSettlementInfo, pRspInfo, nRequestID, bIsLast):
		'''请求查询投资者结算信息响应'''
		print u'Rsp 结算单查询'
		if(self.resp_common(pRspInfo,bIsLast,u'结算单查询')>0):
			self.logger.info(u'结算单查询完成,准备确认')
			try:
				self.logger.info(u'TD:结算单内容:%s' % pSettlementInfo.Content)
			except Exception,inst:
				self.logger.warning(u'TD-ORQSI-A 结算单内容错误:%s' % str(inst))
			self.confirm_settlement_info()
		else:  #这里是未完成分支,需要直接忽略
			try:
				self.logger.info(u'TD:结算单接收中...:%s' % pSettlementInfo.Content)
			except Exception,inst:
				self.logger.warning(u'TD-ORQSI-B 结算单内容错误:%s' % str(inst))
			#self.agent.initialize()
			pass
			
	def OnRspQrySettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
		'''请求查询结算信息确认响应'''
		self.logger.debug(u"TD:结算单确认信息查询响应:rspInfo=%s,结算单确认=%s" % (pRspInfo,pSettlementInfoConfirm))
		#self.query_settlement_info()
		if(self.resp_common(pRspInfo,bIsLast,u'结算单确认情况查询')>0):
			if(pSettlementInfoConfirm == None or int(pSettlementInfoConfirm.ConfirmDate) < self.agent.scur_day):
				#其实这个判断是不对的，如果周日对周五的结果进行了确认，那么周一实际上已经不需要再次确认了
				if(pSettlementInfoConfirm != None):
					self.logger.info(u'TD:最新结算单未确认，需查询后再确认,最后确认时间=%s,scur_day:%s' % (pSettlementInfoConfirm.ConfirmDate,self.agent.scur_day))
				else:
					self.logger.info(u'TD:结算单确认结果为None')
				self.query_settlement_info()
			else:
				self.agent.isSettlementInfoConfirmed = True
				self.logger.info(u'TD:最新结算单已确认，不需再次确认,最后确认时间=%s,scur_day:%s' % (pSettlementInfoConfirm.ConfirmDate,self.agent.scur_day))
				self.agent.initialize()
		
	def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
		'''投资者结算结果确认响应'''
		if(self.resp_common(pRspInfo,bIsLast,u'结算单确认')>0):
			self.agent.isSettlementInfoConfirmed = True
			self.logger.info(u'TD:结算单确认时间: %s-%s' %(pSettlementInfoConfirm.ConfirmDate,pSettlementInfoConfirm.ConfirmTime))
		self.agent.initialize()
		