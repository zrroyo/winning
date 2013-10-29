#-*- coding:utf-8 -*-

import logging
from futures import ApiStruct
#import ctpapi
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
		
	def OnRtnDepthMarketData (self, depth_market_data):
		print "Agent:OnRtnDepthMarketData"
		dp = depth_market_data
		try:
			if dp.LastPrice > 999999 or dp.LastPrice < 10:
				self.logger.warning(u'MD:收到的行情数据有误:%s,LastPrice=:%s' %(dp.InstrumentID,dp.LastPrice))
			if dp.InstrumentID not in self.instruments:
				self.logger.warning(u'MD:收到未订阅的行情:%s' %(dp.InstrumentID,))
				return
			
			#self.logger.debug(u'MD:收到行情，inst=%s,time=%s，volume=%s,last_volume=%s' % (dp.InstrumentID,dp.UpdateTime,dp.Volume,self.last_map[dp.InstrumentID]))
			
			if self.dataMap.isMdDataExisted(dp.InstrumentID):
				print self.dataMap.getMdData(dp.InstrumentID)
				if dp.Volume <= self.dataMap[dp.InstrumentID].Volume:
					#行情未变化
					self.logger.debug(u'MD:行情无变化，inst=%s,time=%s，volume=%s,last_volume=%s' % (dp.InstrumentID,dp.UpdateTime,dp.Volume,self.last_map[dp.InstrumentID]))
					return  
			
				#行情发生变化，记录到行情数据映射中.
				self.dataMap.updateMdData(dp.InstrumentID, dp)
			else:	
				# 合约行情数据还不存在于已知映射中
				self.dataMap.addMdData(dp.InstrumentID, dp)
	
			print u'[%s]，[价：最新/%d，买/%d，卖/%d], [量：买/%d，卖/%d], [最高/%d，最低/%d], 时间：%s' % (dp.InstrumentID, dp.LastPrice, dp.BidPrice1, dp.AskPrice1, dp.BidVolume1, dp.AskVolume1, dp.HighestPrice, dp.LowestPrice, dp.UpdateTime)
		finally:
			self.logger.debug(u'接收行情数据异常!')
			
		pass
		
		
#class TraderAgent:
	#def __init__(self,cuser,instruments,strategy_cfg):
		#'''
		#trader为交易对象
		#tday为当前日,为0则为当日
		#'''
		#self.trader = None
		#self.cuser = cuser
		#self.strategy_cfg = strategy_cfg
		#self.strategy = strategy_cfg.strategy
		##self.instruments = c_instrument.create_instruments(instruments,self.strategy,t2order=t2order)
		#self.instruments = instruments
		#self.request_id = 1
		#self.initialized = False
		#self.front_id = None
		#self.session_id = None
		#self.trading_day = 20110101
		#self.scur_day = int(time.strftime('%Y%m%d')) if tday==0 else tday
		##当前资金/持仓
		#self.available = 0  #可用资金
		###查询命令队列
		#self.qry_commands = []  #每个元素为查询命令，用于初始化时查询相关数据
		#self.init_init()    #init中的init,用于子类的处理
		#self.logger = logging.getLogger('ctp.agent.%s' % self.instruments)
	
		##结算单
		#self.isSettlementInfoConfirmed = False  #结算单未确认
	
	#def initTrader (self, cuser=self.cuser):
		#trader = ctpapi.TraderSpiDelegate(instruments=self.instruments, 
			#broker_id=cuser.broker_id,
			#investor_id= cuser.investor_id,
			#passwd= cuser.passwd,
			#agent = self)
		#trader.Create('trader')
		#trader.SubscribePublicTopic(THOST_TERT_QUICK)
		#trader.SubscribePrivateTopic(THOST_TERT_QUICK)
		#trader.RegisterFront(cuser.port)
		#trader.Init()
		
		#self.trader = trader
		#pass
	
	#def init_init(self):    #init中的init,用于子类的处理
		#pass
	
	#def inc_request_id(self):
		#self.request_id += 1
		#return self.request_id
	    
	#def open_position(self,order):
		#''' 
		#发出下单指令
		#'''
		#req = ApiStruct.InputOrder(
			#InstrumentID = order.instrument,
			#Direction = order.direction,
			#OrderRef = str(order.order_ref),
			#LimitPrice = order.price,   #有个疑问，double类型如何保证舍入舍出，在服务器端取整?
			#VolumeTotalOriginal = order.volume,
			#OrderPriceType = ApiStruct.OPT_LimitPrice,
			
			#BrokerID = self.cuser.broker_id,
			#InvestorID = self.cuser.investor_id,
			#CombOffsetFlag = ApiStruct.OF_Open,         #开仓 5位字符,但是只用到第0位
			#CombHedgeFlag = ApiStruct.HF_Speculation,   #投机 5位字符,但是只用到第0位
	
			#VolumeCondition = ApiStruct.VC_AV,
			#MinVolume = 1,  #这个作用有点不确定,有的文档设成0了
			#ForceCloseReason = ApiStruct.FCC_NotForceClose,
			#IsAutoSuspend = 1,
			#UserForceClose = 0,
			#TimeCondition = ApiStruct.TC_GFD,
		#)
		#self.logger.info(u'下单: instrument=%s,方向=%s,数量=%s,价格=%s' % (order.instrument,u'多' if order.direction==ApiStruct.D_Buy else u'空',order.volume,order.price))
		#r = self.trader.ReqOrderInsert(req,self.inc_request_id())
	
	##def close_position(self,order,CombOffsetFlag = ApiStruct.OF_Close): #Close==CloseYesterday
	#def close_position(self,order,CombOffsetFlag = ApiStruct.OF_CloseToday):
		#''' 
		#发出平仓指令. 默认平今仓
		#是平今还是平昨，可以通过order的mytime解决
		#'''
		#sorder = self.ref2order[order.order_ref].source_order
		#sday = sorder.mytime/1000000    #MMDD
		#cday = self.scur_day % 10000    #MMDD
		#self.logger.info(u'平仓: sday=%s,cday=%s' % (sday,cday))
		#cos_flag = ApiStruct.OF_CloseToday if sday >= cday else ApiStruct.OF_Close    #sday>cday只会在模拟中出现，否则就是穿越了
	
		#req = ApiStruct.InputOrder(
			#InstrumentID = order.instrument,
			#Direction = order.direction,
			#OrderRef = str(order.order_ref),
			#LimitPrice = order.price,
			#VolumeTotalOriginal = order.volume,
			##CombOffsetFlag = CombOffsetFlag,
			#CombOffsetFlag = cos_flag,
			#OrderPriceType = ApiStruct.OPT_LimitPrice,
			
			#BrokerID = self.cuser.broker_id,
			#InvestorID = self.cuser.investor_id,
			#CombHedgeFlag = ApiStruct.HF_Speculation,   #投机 5位字符,但是只用到第0位
	
			#VolumeCondition = ApiStruct.VC_AV,
			#MinVolume = 1,  #TODO:这个有点不确定. 需要测试确认
			#ForceCloseReason = ApiStruct.FCC_NotForceClose,
			#IsAutoSuspend = 1,
			#UserForceClose = 0,
			#TimeCondition = ApiStruct.TC_GFD,
		#)
		#r = self.trader.ReqOrderInsert(req,self.inc_request_id())
	
	#def cancel_command(self,command):
		#'''
		#发出撤单指令
		#'''
		##print 'in cancel command'
		#self.logger.info(u'A_CC:取消命令')
		#req = ApiStruct.InputOrderAction(
			#InstrumentID = command.instrument,
			#OrderRef = str(command.order_ref),
			#BrokerID = self.cuser.broker_id,
			#InvestorID = self.cuser.investor_id,
			#FrontID = self.front_id,
			#SessionID = self.session_id,
			#ActionFlag = ApiStruct.AF_Delete,
			##OrderActionRef = self.inc_order_ref()  #没用,不关心这个，每次撤单成功都需要去查资金
		#)
		#r = self.trader.ReqOrderAction(req,self.inc_request_id())
