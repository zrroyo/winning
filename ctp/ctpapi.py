# -*- coding:utf-8 -*-

import time

import ctperrors
from futures import ApiStruct, MdApi, TraderApi


class CtpMdApi(MdApi):
	"""
	CTP行情数据接口
	"""
	def __init__(self, instruments, broker_id, investor_id, passwd, agent):
		"""
		:param instruments: 合约
		:param broker_id: 期货公司ID
		:param investor_id: 投资者ID
		:param passwd: 口令
		:param agent: 实际操作对象
		"""
		self.instruments = instruments
		self.broker_id = broker_id
		self.investor_id = investor_id
		self.passwd = passwd
		self.agent = agent
		self.logger = agent.logger

	def inc_request_id(self):
		return self.agent.inc_request_id()

	def checkErrorRspInfo(self, info):
		ret = info.ErrorID != 0
		if ret:
			self.logger.error(u"MD:ErrorID:%s,ErrorMsg:%s" % (info.ErrorID, info.ErrorMsg))
		return ret

	def OnRspError(self, info, RequestId, IsLast):
		self.logger.error(u'MD:requestID:%s,IsLast:%s,info:%s' % (RequestId, IsLast, str(info)))

	def OnFrontDisConnected(self, reason):
		self.logger.info(u'MD:front disconnected,reason:%s' % reason)

	def OnFrontConnected(self):
		self.logger.info(u'MD:front connected')
		self.user_login(self.broker_id, self.investor_id, self.passwd)

	def user_login(self, broker_id, investor_id, passwd):
		req = ApiStruct.ReqUserLogin(BrokerID=broker_id, UserID=investor_id, Password=passwd)
		self.ReqUserLogin(req, self.inc_request_id())

	def OnRspUserLogin(self, userlogin, info, rid, is_last):
		if is_last and not self.checkErrorRspInfo(info):
			print("get today's trading day:", repr(self.GetTradingDay()))
			self.SubscribeMarketData(list(self.instruments))

	def OnRtnDepthMarketData(self, depth_market_data):
		self.agent.rtn_depth_market_data(depth_market_data)


class CtpTraderApi(TraderApi):
	"""
	基本CTP交易接口
	"""
	# CTP返回错误的解析接口。因为CTP返回的错误信息为ASCII编码，所以直接通过
	# 错误ID号从本地查找得到错误提示。
	CTP_ERR = ctperrors.CtpError()
			
	def __init__(self, broker_id, investor_id, passwd, agent):
		"""
		:param broker_id: 期货公司ID
		:param investor_id: 投资者ID
		:param passwd: 口令
		:param agent: 实际操作对象
		"""
		self.broker_id = broker_id
		self.investor_id = investor_id
		self.passwd = passwd
		self.agent = agent
		self.is_logged = False
		self.logger = agent.logger

	# 交易服务器端操作接口部分 #

	def isRspSuccess(self, RspInfo):
		return not RspInfo or RspInfo.ErrorID == 0

	def login(self):
		self.logger.info(u'try login...')
		self.user_login(self.broker_id, self.investor_id, self.passwd)

	def OnFrontConnected(self):
		"""
		交易初始化，当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
		"""
		self.logger.info(u'TD:trader front connected')
		self.login()

	def OnFrontDisconnected(self, nReason):
		self.logger.info(u'TD:trader front disconnected,reason=%s' % (nReason,))

	def inc_request_id(self):
		return self.agent.inc_request_id()

	def user_login(self, broker_id, investor_id, passwd):
		req = ApiStruct.ReqUserLogin(BrokerID=broker_id, UserID=investor_id, Password=passwd)
		self.ReqUserLogin(req, self.inc_request_id())

	def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
		self.logger.info(u'TD:trader login')
		self.logger.debug(u"TD:loggin %s" % self.CTP_ERR.formatErrMsg(pRspInfo.ErrorID))
		if not self.isRspSuccess(pRspInfo):
			self.logger.warning('TD:trader login failed, %s' % self.CTP_ERR.formatErrMsg(pRspInfo.ErrorID))
			print(u'综合交易平台登陆失败，请检查网络或用户名/口令')
			self.is_logged = False
			return

		# 交易服务器前端已登录
		self.is_logged = True
		self.logger.info(u'TD:trader login success')
		self.agent.login_success(pRspUserLogin.FrontID, pRspUserLogin.SessionID, pRspUserLogin.MaxOrderRef)
		# self.settlementInfoConfirm()
		# self.agent.set_trading_day(self.GetTradingDay())
		# self.query_settlement_info()
		self.query_settlement_confirm()

	def OnRspUserLogout(self, pUserLogout, pRspInfo, nRequestID, bIsLast):
		"""
		登出请求响应
		"""
		self.logger.info(u'TD:trader logout')
		self.is_logged = False

	def resp_common(self, rsp_info, bIsLast, name='默认'):
		# self.logger.debug("resp: %s" % str(rsp_info))
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
		"""
		结算信息（查询）函数。
		这个基本没用，不如直接确认
		而且需要进一步明确：有史以来第一次确认前查询确认情况还是每天第一次确认查询情况时，返回的响应中
			pSettlementInfoConfirm为空指针. 如果是后者,则建议每日不查询确认情况,或者在generate_struct中对
			CThostFtdcSettlementInfoConfirmField的new_函数进行特殊处理
		CTP写代码的这帮家伙素质太差了，边界条件也不测试，后置断言也不整，空指针乱飞
		2011-3-1 确认每天未确认前查询确认情况时,返回的响应中pSettlementInfoConfirm为空指针
		并且妥善处理空指针之后,仍然有问题,在其中查询结算单无动静
		"""
		req = ApiStruct.QrySettlementInfoConfirm(BrokerID=self.broker_id, InvestorID=self.investor_id)
		self.ReqQrySettlementInfoConfirm(req, self.inc_request_id())

	def query_settlement_info(self):
		# 不填日期表示取上一天结算单,并在响应函数中确认
		self.logger.info(u'TD:取上一日结算单信息并确认,BrokerID=%s,investorID=%s' % (
			self.broker_id, self.investor_id))
		req = ApiStruct.QrySettlementInfo(BrokerID=self.broker_id, InvestorID=self.investor_id, TradingDay=u'')
		time.sleep(1)
		self.ReqQrySettlementInfo(req, self.inc_request_id())

	def confirm_settlement_info(self):
		self.logger.info(u'TD-CSI:准备确认结算单')
		req = ApiStruct.SettlementInfoConfirm(BrokerID=self.broker_id, InvestorID=self.investor_id)
		self.ReqSettlementInfoConfirm(req, self.inc_request_id())

	def OnRspQrySettlementInfo(self, pSettlementInfo, pRspInfo, nRequestID, bIsLast):
		"""
		请求查询投资者结算信息响应
		"""
		if self.resp_common(pRspInfo, bIsLast, u'结算单查询') > 0:
			self.logger.info(u'结算单查询完成,准备确认')
			try:
				self.logger.info(u'TD:结算单内容:%s' % pSettlementInfo.Content)
			except Exception,inst:
				self.logger.warning(u'TD-ORQSI-A 结算单内容错误:%s' % str(inst))
			self.confirm_settlement_info()
		else:
			# 这里是未完成分支,需要直接忽略
			try:
				self.logger.info(u'TD:结算单接收中...:%s' % pSettlementInfo.Content)
			except Exception, e:
				self.logger.warning(u'TD-ORQSI-B 结算单内容错误:%s' % str(e))
			# self.agent.initialize()

	def OnRspQrySettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
		"""
		请求查询结算信息确认响应
		"""
		self.logger.debug(u"TD:结算单确认信息查询响应:rspInfo=%s,结算单确认=%s" % (
			(None if pRspInfo is None else self.CTP_ERR.formatErrMsg(pRspInfo.ErrorID)), pSettlementInfoConfirm))
		# self.query_settlement_info()
		if self.resp_common(pRspInfo, bIsLast, u'结算单确认情况查询') > 0:
			if not pSettlementInfoConfirm or int(pSettlementInfoConfirm.ConfirmDate) < self.agent.scur_day:
				# 其实这个判断是不对的，如果周日对周五的结果进行了确认，那么周一实际上已经不需要再次确认了
				if pSettlementInfoConfirm:
					self.logger.info(u'TD:最新结算单未确认，需查询后再确认,最后确认时间=%s,scur_day:%s' % (
						pSettlementInfoConfirm.ConfirmDate, self.agent.scur_day))
				else:
					self.logger.info(u'TD:结算单确认结果为None')
				self.query_settlement_info()
			else:
				self.agent.isSettlementInfoConfirmed = True
				print(u'TD:最新结算单已确认，不需再次确认,最后确认时间=%s,scur_day:%s' % (
					pSettlementInfoConfirm.ConfirmDate, self.agent.scur_day))
				self.logger.info(u'TD:最新结算单已确认，不需再次确认,最后确认时间=%s,scur_day:%s' % (
					pSettlementInfoConfirm.ConfirmDate, self.agent.scur_day))
				self.agent.initialize()

	def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
		"""
		投资者结算结果确认响应
		"""
		if self.resp_common(pRspInfo, bIsLast, u'结算单确认') > 0:
			self.agent.isSettlementInfoConfirmed = True
			self.logger.info(u'TD:结算单确认时间: %s-%s' %(pSettlementInfoConfirm.ConfirmDate,
								pSettlementInfoConfirm.ConfirmTime))
		self.agent.initialize()

	# 交易准备 #

	def OnRspQryInstrumentMarginRate(self, pInstrumentMarginRate, pRspInfo, nRequestID, bIsLast):
		"""
		保证金率回报。返回的必然是绝对值
		"""
		if bIsLast and self.isRspSuccess(pRspInfo):
			self.agent.rsp_qry_instrument_marginrate(pInstrumentMarginRate)

	def OnRspQryInstrument(self, pInstrument, pRspInfo, nRequestID, bIsLast):
		"""
		合约回报。
		"""
		if bIsLast and self.isRspSuccess(pRspInfo):
			self.agent.rsp_qry_instrument(pInstrument)
		else:
			# 模糊查询的结果，获得了多个合约的数据，只有最后一个的bLast是True
			self.agent.rsp_qry_instrument(pInstrument)

	def OnRspQryTradingAccount(self, pTradingAccount, pRspInfo, nRequestID, bIsLast):
		"""
		请求查询资金账户响应
		"""
		self.logger.info(u'TD:资金账户响应:%s' % pTradingAccount)
		if bIsLast and self.isRspSuccess(pRspInfo):
			self.agent.rsp_qry_trading_account(pTradingAccount)

	def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
		"""
		请求查询投资者持仓响应
		"""
		# 每次一个单独的数据报
		if self.isRspSuccess(pRspInfo):
			self.agent.rsp_qry_position(pInvestorPosition)

	def OnRspQryInvestorPositionDetail(self, pInvestorPositionDetail, pRspInfo, nRequestID, bIsLast):
		"""
		请求查询投资者持仓明细响应
		"""
		self.logger.info(str(pInvestorPositionDetail))
		# 每次一个单独的数据报
		if self.isRspSuccess(pRspInfo):
			self.agent.rsp_qry_position_detail(pInvestorPositionDetail)

	def OnRspError(self, info, RequestId, IsLast):
		"""
		错误应答
		"""
		self.logger.error(u'TD:requestID:%s,IsLast:%s,info:%s' % (RequestId, IsLast, str(info)))

	def OnRspQryOrder(self, pOrder, pRspInfo, nRequestID, bIsLast):
		"""
		请求查询报单响应
		"""
		if bIsLast and self.isRspSuccess(pRspInfo):
			self.agent.rsp_qry_order(pOrder)
		else:
			self.logger.error(u'TD:requestID:%s,IsLast:%s,info:%s' % (nRequestID, bIsLast, str(pRspInfo)))

	def OnRspQryTrade(self, pTrade, pRspInfo, nRequestID, bIsLast):
		"""
		请求查询成交响应
		"""
		if bIsLast and self.isRspSuccess(pRspInfo):
			self.agent.rsp_qry_trade(pTrade)

	# 交易操作部分 #

	def OnRspOrderInsert(self, pInputOrder, pRspInfo, nRequestID, bIsLast):
		"""
		报单未通过参数校验,被CTP拒绝
		正常情况后不应该出现
		"""
		self.logger.warning(u'TD:CTP报单录入错误回报, 正常后不应该出现,rspInfo=%s' %
				self.CTP_ERR.formatErrMsg(pRspInfo.ErrorID))
		# self.logger.warning(u'报单校验错误,ErrorID=%s,ErrorMsg=%s,pRspInfo=%s,bIsLast=%s' % (
		# 	pRspInfo.ErrorID, pRspInfo.ErrorMsg, str(pRspInfo), bIsLast))
		# self.agent.rsp_order_insert(pInputOrder.OrderRef, pInputOrder.InstrumentID, pRspInfo.ErrorID, pRspInfo.ErrorMsg)
		self.agent.err_order_insert(pInputOrder)

	def OnErrRtnOrderInsert(self, pInputOrder, pRspInfo):
		"""
		交易所报单录入错误回报
		正常情况后不应该出现
		这个回报因为没有request_id,所以没办法对应
		"""
		self.logger.warning(u'TD:交易所报单录入错误回报, 正常后不应该出现,rspInfo=%s'%
				self.CTP_ERR.formatErrMsg(pRspInfo.ErrorID))
		# self.agent.err_order_insert(pInputOrder.OrderRef, pInputOrder.InstrumentID, pRspInfo.ErrorID, pRspInfo.ErrorMsg)

	def OnRtnOrder(self, pOrder):
		"""
		报单通知
		CTP、交易所接受报单
		Agent中不区分，所得信息只用于撤单
		"""
		self.logger.info(u'报单响应,OrderStatus=%s, OrderRef=%s' % (str(pOrder.OrderStatus), str(pOrder.OrderRef)))
		if pOrder.OrderStatus == 'a':
			self.logger.info(u'TD:CTP接受Order，但未发到交易所, BrokerID=%s,BrokerOrderSeq = %s,TraderID=%s,OrderLocalID=%s' % (
				pOrder.BrokerID, pOrder.BrokerOrderSeq, pOrder.TraderID, pOrder.OrderLocalID))
		else:
			self.logger.info(u'TD:交易所接受Order,exchangeID=%s,OrderSysID=%s,TraderID=%s, OrderLocalID=%s' % (
				pOrder.ExchangeID, pOrder.OrderSysID, pOrder.TraderID, pOrder.OrderLocalID))

		self.agent.rtn_order(pOrder)

	def OnRtnTrade(self, pTrade):
		"""
		成交通知
		"""
		self.logger.info(u'TD:成交通知,BrokerID=%s,BrokerOrderSeq = %s,exchangeID=%s,OrderSysID=%s,TraderID=%s,OrderLocalID=%s' %(
			pTrade.BrokerID, pTrade.BrokerOrderSeq, pTrade.ExchangeID, pTrade.OrderSysID, pTrade.TraderID, pTrade.OrderLocalID))
		self.logger.info(u'TD:成交回报,Trade=%s' % repr(pTrade))
		self.agent.rtn_trade(pTrade)

	def OnRspOrderAction(self, pInputOrderAction, pRspInfo, nRequestID, bIsLast):
		"""
		ctp撤单校验错误
		"""
		self.logger.warning(u'TD:CTP撤单录入错误回报, 正常后不应该出现,rspInfo=%s' % self.CTP_ERR.formatErrMsg(pRspInfo.ErrorID))
		self.agent.err_order_action(pInputOrderAction)

	def OnErrRtnOrderAction(self, pOrderAction, pRspInfo):
		"""
		交易所撤单操作错误回报
		正常情况后不应该出现
		"""
		self.logger.warning(u'TD:交易所撤单录入错误回报, 可能已经成交,rspInfo=%s'% self.CTP_ERR.formatErrMsg(pRspInfo.ErrorID))
		# self.agent.err_order_action(pOrderAction.OrderRef, pOrderAction.InstrumentID, pRspInfo.ErrorID, pRspInfo.ErrorMsg)

	# Agent操作接口部分 #

	def open_position(self, instrument, direction, order_ref, price, volume):
		"""
		下单、开仓
		:param instrument: 合约代号
		:param direction: 方向
		:param order_ref:
		:param price: 价格
		:param volume: 开仓数量
		"""
		req = ApiStruct.InputOrder(
			InstrumentID=instrument,
			Direction=direction,
			OrderRef=str(order_ref),
			LimitPrice=price,   # 有个疑问，double类型如何保证舍入舍出，在服务器端取整?
			VolumeTotalOriginal=volume,
			OrderPriceType=ApiStruct.OPT_LimitPrice,

			BrokerID=self.broker_id,
			InvestorID=self.investor_id,
			CombOffsetFlag=ApiStruct.OF_Open,         # 开仓 5位字符,但是只用到第0位
			CombHedgeFlag=ApiStruct.HF_Speculation,   # 投机 5位字符,但是只用到第0位

			VolumeCondition=ApiStruct.VC_AV,
			MinVolume=1,  # 这个作用有点不确定,有的文档设成0了
			ForceCloseReason=ApiStruct.FCC_NotForceClose,
			IsAutoSuspend=1,
			UserForceClose=0,
			ContingentCondition=ApiStruct.CC_Immediately,
			TimeCondition=ApiStruct.TC_GFD
			)
		self.logger.info(u'下单: instrument=%s,方向=%s,数量=%s,价格=%s' % (
			instrument, u'多' if direction == ApiStruct.D_Buy else u'空', volume, price))
		self.ReqOrderInsert(req, self.inc_request_id())
		
	def close_position(self, instrument, direction, order_ref, price, volume, cos_flag):
		"""
		平仓
		发出平仓指令. 默认平今仓
		是平今还是平昨，可以通过order的mytime解决
		:param instrument: 合约代号
		:param direction: 方向
		:param order_ref:
		:param price: 价格
		:param volume: 开仓数量
		:param cos_flag:
		"""
		# sorder = self.ref2order[order.order_ref].source_order
		# sday = sorder.mytime/1000000    # MMDD
		# cday = self.scur_day % 10000    # MMDD
		# cos_flag = ApiStruct.OF_CloseToday if sday >= cday else ApiStruct.OF_Close  # sday>cday只会在模拟中出现，否则就是穿越了

		req = ApiStruct.InputOrder(
			InstrumentID=instrument,
			Direction=direction,
			OrderRef=str(order_ref),
			LimitPrice=price,
			VolumeTotalOriginal=volume,
			#CombOffsetFlag=CombOffsetFlag,
			CombOffsetFlag=cos_flag,
			OrderPriceType=ApiStruct.OPT_LimitPrice,

			BrokerID=self.broker_id,
			InvestorID=self.investor_id,
			CombHedgeFlag=ApiStruct.HF_Speculation,   # 投机 5位字符,但是只用到第0位

			VolumeCondition=ApiStruct.VC_AV,
			MinVolume=1,  # TODO:这个有点不确定. 需要测试确认
			ForceCloseReason=ApiStruct.FCC_NotForceClose,
			IsAutoSuspend=1,
			UserForceClose=0,
			ContingentCondition=ApiStruct.CC_Immediately,
			TimeCondition=ApiStruct.TC_GFD,
		)
		self.logger.info(u'平仓: instrument=%s,方向=%s,数量=%s,价格=%s' % (
			instrument,u'空' if direction == ApiStruct.D_Sell else u'多', volume, price))
		self.ReqOrderInsert(req, self.inc_request_id())
			
	def cancel_command(self, instrument, order_ref):
		"""
		发出撤单指令
		:param instrument: 合约代号
		:param order_ref: 本地报单编号
		"""
		self.logger.info(u'A_CC:撤消报单: %s, OrderRef %d' % (instrument, order_ref))
		req = ApiStruct.InputOrderAction(
			InstrumentID=instrument,
			OrderRef=str(order_ref),
			BrokerID=self.broker_id,
			InvestorID=self.investor_id,
			FrontID=self.agent.front_id,
			SessionID=self.agent.session_id,
			ActionFlag=ApiStruct.AF_Delete,
			# OrderActionRef=self.inc_order_ref()  # 没用,不关心这个，每次撤单成功都需要去查资金
		)
		self.ReqOrderAction(req, self.inc_request_id())
			
	def query_order(self, instrument, order_sys_id):
		"""
		查询报单
		:param instrument: 合约代号
		:param order_sys_id: 交易服务器端报单编号
		"""
		req = ApiStruct.QryOrder(
			BrokerID=self.broker_id,
			InvestorID=self.investor_id,
			InstrumentID=instrument,
			OrderSysID=str(order_sys_id),
		)
		self.logger.info(u'查询下单: %s, OrderRef %s' % (instrument, order_sys_id))
		self.ReqQryOrder(req, self.inc_request_id())
