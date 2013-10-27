#-*- coding:utf-8 -*-

import logging
from futures import ApiStruct, MdApi, TraderApi

class CtpMdApi(MdApi):
	logger = logging.getLogger('ctp.CtpMdApi')
	
	def __init__(self, instruments, broker_id,
			investor_id, passwd, *args,**kwargs):
		self.requestid=0
		self.instruments = instruments
		self.broker_id =broker_id
		self.investor_id = investor_id
		self.passwd = passwd
	
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
		print "OnRtnDepthMarketData"
		##print depth_market_data.BidPrice1,depth_market_data.BidVolume1,depth_market_data.AskPrice1,depth_market_data.AskVolume1,depth_market_data.LastPrice,depth_market_data.Volume,depth_market_data.UpdateTime,depth_market_data.UpdateMillisec,depth_market_data.InstrumentID	
		try:
			if depth_market_data.LastPrice > 999999 or depth_market_data.LastPrice < 10:
				self.logger.warning(u'MD:收到的行情数据有误:%s,LastPrice=:%s' %(depth_market_data.InstrumentID,depth_market_data.LastPrice))
			if depth_market_data.InstrumentID not in self.instruments:
				self.logger.warning(u'MD:收到未订阅的行情:%s' %(depth_market_data.InstrumentID,))
	
			dp = depth_market_data
			#self.logger.debug(u'MD:收到行情，inst=%s,time=%s，volume=%s,last_volume=%s' % (dp.InstrumentID,dp.UpdateTime,dp.Volume,self.last_map[dp.InstrumentID]))
			#if dp.Volume <= self.last_map[dp.InstrumentID]:
				#self.logger.debug(u'MD:行情无变化，inst=%s,time=%s，volume=%s,last_volume=%s' % (dp.InstrumentID,dp.UpdateTime,dp.Volume,self.last_map[dp.InstrumentID]))
				#return  #行情未变化
			
			#self.last_map[dp.InstrumentID] = dp.Volume
			
			#self.agent.inc_tick()
			#ctick = self.market_data2tick(depth_market_data)
			#print ctick
			#self.agent.RtnTick(ctick)
			
			print depth_market_data.BidPrice1,depth_market_data.BidVolume1,depth_market_data.AskPrice1,depth_market_data.AskVolume1,depth_market_data.LastPrice,depth_market_data.Volume,depth_market_data.UpdateTime,depth_market_data.UpdateMillisec,depth_market_data.InstrumentID	
		finally:
			pass
			
	#def market_data2tick(self,market_data):
		##market_data的格式转换和整理, 交易数据都转换为整数
		#try:
			##rev的后四个字段在模拟行情中经常出错
			#rev = BaseObject(instrument = market_data.InstrumentID,date=self.agent.scur_day,bid_price=0,bid_volume=0,ask_price=0,ask_volume=0)
			#rev.min1 = int(market_data.UpdateTime[:2]+market_data.UpdateTime[3:5])
			#rev.sec = int(market_data.UpdateTime[-2:])
			#rev.msec = int(market_data.UpdateMillisec)
			#rev.holding = int(market_data.OpenInterest+0.1)
			#rev.dvolume = market_data.Volume
			#rev.price = int(market_data.LastPrice*10+0.1)
			#rev.high = int(market_data.HighestPrice*10+0.1)
			#rev.low = int(market_data.LowestPrice*10+0.1)
			#rev.bid_price = int(market_data.BidPrice1*10+0.1)
			#rev.bid_volume = market_data.BidVolume1
			#rev.ask_price = int(market_data.AskPrice1*10+0.1)
			#rev.ask_volume = market_data.AskVolume1
			
			#if len(market_data.TradingDay.strip()) > 0:
				#rev.date = int(market_data.TradingDay)
			#else:#有时候会有错
				#rev.date = self.last_day
				
			#rev.time = rev.date%10000 * 1000000+ rev.min1*100 + rev.sec
			#rev.switch_min = False  #分钟切换
			#self.last_day = rev.date
		#except Exception,inst:
			#self.logger.warning(u'MD:%s 行情数据转换错误:%s,updateTime="%s",msec="%s",tday="%s"' % (market_data.InstrumentID,str(inst),market_data.UpdateTime,market_data.UpdateMillisec,market_data.TradingDay))
		#return rev
		