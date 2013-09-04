#-*- coding:utf-8 -*-

import logging
from futures import ApiStruct, MdApi, TraderApi
import ctpagent
import instrument

#日内最后交易时间，超过为越界
LAST_TRADE_TIME = 1515

#数据定义中唯一一个enum
THOST_TERT_RESTART  = ApiStruct.TERT_RESTART
THOST_TERT_RESUME   = ApiStruct.TERT_RESUME
THOST_TERT_QUICK    = ApiStruct.TERT_QUICK

class MdSpiDelegate(MdApi):
	'''
		将行情信息转发到Agent
		并自行处理杂务
	'''
	logger = logging.getLogger('ctp.MdSpiDelegate')
	
	last_map = {}
	
	def __init__(self,
		instruments, #合约映射 name ==>c_instrument
		broker_id,   #期货公司ID
		investor_id, #投资者ID
		passwd, #口令
		agent,  #实际操作对象
		):        
		self.instruments = set([name for name in instruments])
		self.broker_id =broker_id
		self.investor_id = investor_id
		self.passwd = passwd
		self.agent = agent
		##必须在每日重新连接时初始化它. 这一点用到了生产行情服务器收盘后关闭的特点(模拟的不关闭)
		MdSpiDelegate.last_map = dict([(id,0) for id in instruments])
		self.last_day = 0
		agent.add_mdapi(self)
		
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
		r=self.ReqUserLogin(req,self.agent.inc_request_id())

	def OnRspUserLogin(self, userlogin, info, rid, is_last):
		self.logger.info(u'MD:user login,info:%s,rid:%s,is_last:%s' % (info,rid,is_last))
		scur_day = int(time.strftime('%Y%m%d'))
		if scur_day > self.agent.scur_day:    #换日,重新设置volume
			self.logger.info(u'MD:换日, %s-->%s' % (self.agent.scur_day,scur_day))
			#self.agent.scur_day = scur_day
			self.agent.day_switch(scur_day)
			MdSpiDelegate.last_map = dict([(id,0) for id in self.instruments])
		
		if is_last and not self.checkErrorRspInfo(info):
			self.logger.info(u"MD:get today's trading day:%s" % repr(self.GetTradingDay()))
			self.subscribe_market_data(self.instruments)

	def subscribe_market_data(self, instruments):
		self.SubscribeMarketData(list(instruments))

	def OnRtnDepthMarketData(self, depth_market_data):
		try:
			#mylock.acquire()
			#self.logger.debug(u'获得锁.................,mylock.id=%s' % id(mylock))        
			if depth_market_data.LastPrice > 999999 or depth_market_data.LastPrice < 10:
				self.logger.warning(u'MD:收到的行情数据有误:%s,LastPrice=:%s' %(depth_market_data.InstrumentID,depth_market_data.LastPrice))
			if depth_market_data.InstrumentID not in self.instruments:
				self.logger.warning(u'MD:收到未订阅的行情:%s' %(depth_market_data.InstrumentID,))
			#self.logger.debug(u'收到行情:%s,time=%s:%s' %(depth_market_data.InstrumentID,depth_market_data.UpdateTime,depth_market_data.UpdateMillisec))
			dp = depth_market_data
			self.logger.debug(u'MD:收到行情，inst=%s,time=%s，volume=%s,last_volume=%s' % (dp.InstrumentID,dp.UpdateTime,dp.Volume,self.last_map[dp.InstrumentID]))
			if dp.Volume <= self.last_map[dp.InstrumentID]:
				self.logger.debug(u'MD:行情无变化，inst=%s,time=%s，volume=%s,last_volume=%s' % (dp.InstrumentID,dp.UpdateTime,dp.Volume,self.last_map[dp.InstrumentID]))
				return  #行情未变化
			self.last_map[dp.InstrumentID] = dp.Volume
			#mylock.release()   #至此已经去掉重复的数据
		
			#self.logger.debug(u'after modify instrument=%s,lastvolume:%s,curVolume:%s' % (dp.InstrumentID,self.last_map[dp.InstrumentID],dp.Volume))
			#self.logger.debug(u'before loop')
			self.agent.inc_tick()
			ctick = self.market_data2tick(depth_market_data)
			self.agent.RtnTick(ctick)
		finally:
			pass
		
		if self.agent.save_flag == True:
			ff = open(hreader.make_tick_filename(ctick.instrument),'a+')
			try:
				ff.write(u'%(instrument)s,%(date)s,%(min1)s,%(sec)s,%(msec)s,%(holding)s,%(dvolume)s,%(price)s,%(high)s,%(low)s,%(bid_price)s,%(bid_volume)s,%(ask_price)s,%(ask_volume)s\n' % ctick.__dict__)
			except Exception,inst:
				print str(depth_market_data),str(depth_market_data.TradingDay),str(depth_market_data.UpdateTime)
			ff.close()

	def market_data2tick(self,market_data):
		#market_data的格式转换和整理, 交易数据都转换为整数
		try:
			#rev的后四个字段在模拟行情中经常出错
			rev = BaseObject(instrument = market_data.InstrumentID,date=self.agent.scur_day,bid_price=0,bid_volume=0,ask_price=0,ask_volume=0)
			rev.min1 = int(market_data.UpdateTime[:2]+market_data.UpdateTime[3:5])
			rev.sec = int(market_data.UpdateTime[-2:])
			rev.msec = int(market_data.UpdateMillisec)
			rev.holding = int(market_data.OpenInterest+0.1)
			rev.dvolume = market_data.Volume
			rev.price = int(market_data.LastPrice*10+0.1)
			rev.high = int(market_data.HighestPrice*10+0.1)
			rev.low = int(market_data.LowestPrice*10+0.1)
			rev.bid_price = int(market_data.BidPrice1*10+0.1)
			rev.bid_volume = market_data.BidVolume1
			rev.ask_price = int(market_data.AskPrice1*10+0.1)
			rev.ask_volume = market_data.AskVolume1
			if len(market_data.TradingDay.strip()) > 0:
				rev.date = int(market_data.TradingDay)
			else:#有时候会有错
				rev.date = self.last_day    
			rev.time = rev.date%10000 * 1000000+ rev.min1*100 + rev.sec
			rev.switch_min = False  #分钟切换
			self.last_day = rev.date
		except Exception,inst:
			#self.logger.warning(u'MD:行情数据转换错误:%s' % str(inst))
			self.logger.warning(u'MD:%s 行情数据转换错误:%s,updateTime="%s",msec="%s",tday="%s"' % (market_data.InstrumentID,str(inst),market_data.UpdateTime,market_data.UpdateMillisec,market_data.TradingDay))
		
		return rev

class TraderSpiDelegate(TraderApi):
	'''
		将服务器回应转发到Agent
		并自行处理杂务
	'''
	logger = logging.getLogger('ctp.TraderSpiDelegate')    
	def __init__(self,
		instruments, #合约映射 name ==>c_instrument 
		broker_id,   #期货公司ID
		investor_id, #投资者ID
		passwd, #口令
		agent,  #实际操作对象
		):        
		self.instruments = set([name for name in instruments])
		self.broker_id =broker_id
		self.investor_id = investor_id
		self.passwd = passwd
		self.agent = agent
		self.agent.set_spi(self)
		self.is_logged = False
	
	def isRspSuccess(self,RspInfo):
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
		r=self.ReqUserLogin(req,self.agent.inc_request_id())
	
	def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
		self.logger.info(u'TD:trader login')
		self.logger.debug(u"TD:loggin %s" % str(pRspInfo))
		if not self.isRspSuccess(pRspInfo):
			self.logger.warning(u'TD:trader login failed, errMsg=%s' %(pRspInfo.ErrorMsg,))
			print u'综合交易平台登陆失败，请检查网络或用户名/口令'
			self.is_logged = False
			return
		
		self.is_logged = True
		self.logger.info(u'TD:trader login success')
		self.agent.login_success(pRspUserLogin.FrontID,pRspUserLogin.SessionID,pRspUserLogin.MaxOrderRef)
		#self.settlementInfoConfirm()
		self.agent.set_trading_day(self.GetTradingDay())
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
	
	###交易准备
	def OnRspQryInstrumentMarginRate(self, pInstrumentMarginRate, pRspInfo, nRequestID, bIsLast):
		'''
		保证金率回报。返回的必然是绝对值
		'''
		if bIsLast and self.isRspSuccess(pRspInfo):
			self.agent.rsp_qry_instrument_marginrate(pInstrumentMarginRate)
		else:
			#logging
			pass

	def OnRspQryInstrument(self, pInstrument, pRspInfo, nRequestID, bIsLast):
		'''
		合约回报。
		'''
		if bIsLast and self.isRspSuccess(pRspInfo):
			self.agent.rsp_qry_instrument(pInstrument)
			#print pInstrument
		else:
			#logging
			#print pInstrument
			self.agent.rsp_qry_instrument(pInstrument)  #模糊查询的结果,获得了多个合约的数据，只有最后一个的bLast是True


	def OnRspQryTradingAccount(self, pTradingAccount, pRspInfo, nRequestID, bIsLast):
		'''
		请求查询资金账户响应
		'''
		print u'查询资金账户响应'
		self.logger.info(u'TD:资金账户响应:%s' % pTradingAccount)
		if bIsLast and self.isRspSuccess(pRspInfo):
			self.agent.rsp_qry_trading_account(pTradingAccount)
		else:
			#logging
			pass

	def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
		'''请求查询投资者持仓响应'''
		#print u'查询持仓响应',str(pInvestorPosition),str(pRspInfo)
		if self.isRspSuccess(pRspInfo): #每次一个单独的数据报
			self.agent.rsp_qry_position(pInvestorPosition)
		else:
			#logging
			pass

	def OnRspQryInvestorPositionDetail(self, pInvestorPositionDetail, pRspInfo, nRequestID, bIsLast):
		'''请求查询投资者持仓明细响应'''
		logging.info(str(pInvestorPositionDetail))
		if self.isRspSuccess(pRspInfo): #每次一个单独的数据报
			self.agent.rsp_qry_position_detail(pInvestorPositionDetail)
		else:
			#logging
			pass

	def OnRspError(self, info, RequestId, IsLast):
		''' 错误应答
		'''
		self.logger.error(u'TD:requestID:%s,IsLast:%s,info:%s' % (RequestId,IsLast,str(info)))

	def OnRspQryOrder(self, pOrder, pRspInfo, nRequestID, bIsLast):
		'''请求查询报单响应'''
		if bIsLast and self.isRspSuccess(pRspInfo):
			self.agent.rsp_qry_order(pOrder)
		else:
			self.logger.error(u'TD:requestID:%s,IsLast:%s,info:%s' % (nRequestID,bIsLast,str(pRspInfo)))
			pass

	def OnRspQryTrade(self, pTrade, pRspInfo, nRequestID, bIsLast):
		'''请求查询成交响应'''
		if bIsLast and self.isRspSuccess(pRspInfo):
			self.agent.rsp_qry_trade(pTrade)
		else:
			#logging
			pass

	###交易操作
	def OnRspOrderInsert(self, pInputOrder, pRspInfo, nRequestID, bIsLast):
		'''
		报单未通过参数校验,被CTP拒绝
		正常情况后不应该出现
		'''
		print pRspInfo,nRequestID
		self.logger.warning(u'TD:CTP报单录入错误回报, 正常后不应该出现,rspInfo=%s'%(str(pRspInfo),))
		#self.logger.warning(u'报单校验错误,ErrorID=%s,ErrorMsg=%s,pRspInfo=%s,bIsLast=%s' % (pRspInfo.ErrorID,pRspInfo.ErrorMsg,str(pRspInfo),bIsLast))
		#self.agent.rsp_order_insert(pInputOrder.OrderRef,pInputOrder.InstrumentID,pRspInfo.ErrorID,pRspInfo.ErrorMsg)
		self.agent.err_order_insert(pInputOrder.OrderRef,pInputOrder.InstrumentID,pRspInfo.ErrorID,pRspInfo.ErrorMsg)
	
	def OnErrRtnOrderInsert(self, pInputOrder, pRspInfo):
		'''
		交易所报单录入错误回报
		正常情况后不应该出现
		这个回报因为没有request_id,所以没办法对应
		'''
		print u'ERROR Order Insert'
		self.logger.warning(u'TD:交易所报单录入错误回报, 正常后不应该出现,rspInfo=%s'%(str(pRspInfo),))
		self.agent.err_order_insert(pInputOrder.OrderRef,pInputOrder.InstrumentID,pRspInfo.ErrorID,pRspInfo.ErrorMsg)
    
	def OnRtnOrder(self, pOrder):
		''' 报单通知
		CTP、交易所接受报单
		Agent中不区分，所得信息只用于撤单
		'''
		#print repr(pOrder)
		self.logger.info(u'报单响应,Order=%s' % str(pOrder))
		if pOrder.OrderStatus == 'a':
			#CTP接受，但未发到交易所
			#print u'CTP接受Order，但未发到交易所, BrokerID=%s,BrokerOrderSeq = %s,TraderID=%s, OrderLocalID=%s' % (pOrder.BrokerID,pOrder.BrokerOrderSeq,pOrder.TraderID,pOrder.OrderLocalID)
			self.logger.info(u'TD:CTP接受Order，但未发到交易所, BrokerID=%s,BrokerOrderSeq = %s,TraderID=%s, OrderLocalID=%s' % (pOrder.BrokerID,pOrder.BrokerOrderSeq,pOrder.TraderID,pOrder.OrderLocalID))
			self.agent.rtn_order(pOrder)
		else:
			#print u'交易所接受Order,exchangeID=%s,OrderSysID=%s,TraderID=%s, OrderLocalID=%s' % (pOrder.ExchangeID,pOrder.OrderSysID,pOrder.TraderID,pOrder.OrderLocalID)
			self.logger.info(u'TD:交易所接受Order,exchangeID=%s,OrderSysID=%s,TraderID=%s, OrderLocalID=%s' % (pOrder.ExchangeID,pOrder.OrderSysID,pOrder.TraderID,pOrder.OrderLocalID))
			#self.agent.rtn_order_exchange(pOrder)
			self.agent.rtn_order(pOrder)

	def OnRtnTrade(self, pTrade):
		'''成交通知'''
		self.logger.info(u'TD:成交通知,BrokerID=%s,BrokerOrderSeq = %s,exchangeID=%s,OrderSysID=%s,TraderID=%s, OrderLocalID=%s' %(pTrade.BrokerID,pTrade.BrokerOrderSeq,pTrade.ExchangeID,pTrade.OrderSysID,pTrade.TraderID,pTrade.OrderLocalID))
		self.logger.info(u'TD:成交回报,Trade=%s' % repr(pTrade))
		self.agent.rtn_trade(pTrade)
	
	def OnRspOrderAction(self, pInputOrderAction, pRspInfo, nRequestID, bIsLast):
		'''
		ctp撤单校验错误
		'''
		self.logger.warning(u'TD:CTP撤单录入错误回报, 正常后不应该出现,rspInfo=%s'%(str(pRspInfo),))
		#self.agent.rsp_order_action(pInputOrderAction.OrderRef,pInputOrderAction.InstrumentID,pRspInfo.ErrorID,pRspInfo.ErrorMsg)
		self.agent.err_order_action(pInputOrderAction.OrderRef,pInputOrderAction.InstrumentID,pRspInfo.ErrorID,pRspInfo.ErrorMsg)
	
	def OnErrRtnOrderAction(self, pOrderAction, pRspInfo):
		''' 
		交易所撤单操作错误回报
		正常情况后不应该出现
		'''
		self.logger.warning(u'TD:交易所撤单录入错误回报, 可能已经成交,rspInfo=%s'%(str(pRspInfo),))
		self.agent.err_order_action(pOrderAction.OrderRef,pOrderAction.InstrumentID,pRspInfo.ErrorID,pRspInfo.ErrorMsg)


