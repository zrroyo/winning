#-*- coding:utf-8 -*-

import sys
sys.path.append('..')
import logging
import time
import thread
from futures import ApiStruct
from ctpapi import CtpMdApi, CtpTraderApi
from misc.elemmap import ElementMap
from mdtolocal import MarketDataAccess
from misc.futcom import tempNameSuffix

'''
CTP日志管理
'''
logName = 'ctp%s.log' % tempNameSuffix()
loggingInited = False

#初始化CTP日志接口
def initLoggingBasic():
	global loggingInited
	
	#如果还没完成初始化，则进行初始化
	if loggingInited == False:
		logging.basicConfig(filename=logName,level=logging.INFO,format='%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
		loggingInited = True
		
#行情数据服务器端代理
class MarketDataAgent:
	def __init__ (self,
		instruments, 	#合约 
		broker_id,   	#期货公司ID
		investor_id, 	#投资者ID
		passwd,	 	#口令
		server_port	#交易服务器端口
		):
		
		self.instruments = instruments
		self.broker_id = broker_id
		self.investor_id = investor_id
		self.passwd = passwd
		self.server_port = server_port
		
		self.request_id = 1
		
		self.dataMap = ElementMap()	#行情记录映射表
		self.mdlocal = MarketDataAccess(self.dataMap)	#初始化行情访问接口
		
	# 在开始行情服务前必须被调用	
	def init_init (self):
		#初始化日志接口
		initLoggingBasic()
			
		self.logger = logging.getLogger('Md')
			
		#初始化CTP行情接口
		mdSpi = CtpMdApi(self.instruments, self.broker_id, self.investor_id, self.passwd, self)
		mdSpi.Create("MarketDataAgent")
		mdSpi.RegisterFront(self.server_port)
		mdSpi.Init()
		self.mdspi = mdSpi
			
	def inc_request_id (self):
		self.request_id += 1
		return self.request_id
		
	# CtpMdApi对象OnRtnDepthMarketData成员方法的真实回调函数	
	def rtn_depth_market_data (self, depth_market_data):
		#print "Agent:OnRtnDepthMarketData"
		dp = depth_market_data
		try:
			if dp.LastPrice > 999999 or dp.LastPrice < 10:
				self.logger.warning(u'MD:收到的行情数据有误:%s,LastPrice=:%s' %(dp.InstrumentID,dp.LastPrice))
			if dp.InstrumentID not in self.instruments:
				self.logger.warning(u'MD:收到未订阅的行情:%s' %(dp.InstrumentID,))
				return
			
			if self.dataMap.isElementExisted(dp.InstrumentID):
				##已接受过该合约行情，如果行情发生改变则更新映射
				##print dp.Volume, self.dataMap.getMdData(dp.InstrumentID).Volume
				#if dp.Volume <= self.dataMap.getElement(dp.InstrumentID).Volume:
					##行情未变化
					##self.logger.debug(u'MD:行情无变化，inst=%s,time=%s，volume=%s,last_volume=%s' % (dp.InstrumentID,dp.UpdateTime,dp.Volume,self.dataMap.getMdData(dp.InstrumentID).Volume))
					#return 
			
				#行情发生变化，记录到行情数据映射中.
				self.dataMap.updateElement(dp.InstrumentID, dp)
			else:	
				#合约行情数据还不存在于已知映射中
				self.dataMap.addElement(dp.InstrumentID, dp)
	
			#print u'[%s]，[价：最新/%g，买/%g，卖/%g], [量：买/%d，卖/%d，总：%d], [最高/%d，最低/%d], 时间：%s' % (dp.InstrumentID, dp.LastPrice, dp.BidPrice1, dp.AskPrice1, dp.BidVolume1, dp.AskVolume1, dp.Volume, dp.HighestPrice, dp.LowestPrice, dp.UpdateTime)
		finally:
			self.logger.debug(u'接收行情数据异常!')
		
	#显示／描绘内容池里边的所有内容
	def __display (self, poll, painter, window, lineStart=0):
		keys = poll.keys()
		keys.sort()	#排序后输出
		#print keys
		
		i = lineStart
		for k in keys:
			try:
				#print k, poll[k]
				dp = poll[k]
				output = '[%6s %s%3d][Price: N/%g, B/%g, S/%g],[Vol: B/%d, S/%d, T/%d],[H/%g, L/%g],[%s]' % (dp.InstrumentID, ('↑' if dp.LastPrice > dp.PreClosePrice else '↓'), (dp.LastPrice - dp.PreClosePrice if dp.LastPrice > dp.PreClosePrice else dp.PreClosePrice - dp.LastPrice), dp.LastPrice, dp.BidPrice1, dp.AskPrice1, dp.BidVolume1, dp.AskVolume1, dp.Volume, dp.HighestPrice, dp.LowestPrice, dp.UpdateTime)
				#output = '[%7s][价：新/%g，买/%g，卖/%g],[量：买/%g，卖/%g，总/%g],[高/%g，低/%g],[%s]' % (dp.InstrumentID, dp.LastPrice, dp.BidPrice1, dp.AskPrice1, dp.BidVolume1, dp.AskVolume1, dp.Volume, dp.HighestPrice, dp.LowestPrice, dp.UpdateTime)
				#print output
				painter.paintLine(window, i, output)
				i += 1
			except:
				print 'Painter Exception'
				#painter.destroy()
				#pass
		
		#window.refresh()
			
	#启动行情监视器
	def start_monitor (self, 
		painter, 	#终端描绘对象
		window		#curses窗口
		):
		try:
			while 1:
				self.__display(self.dataMap.elemDict, painter, window)
				time.sleep(0.5)
		except:
			painter.destroy()
		
#交易服务器端代理
class TraderAgent:
	def __init__ (self,
		broker_id,   	#期货公司ID
		investor_id, 	#投资者ID
		passwd,	 	#口令
		server_port	#交易服务器端口
		):
		'''
		trader为交易对象
		tday为当前日,为0则为当日
		'''
		self.request_id = 1
		self.request_lock = thread.allocate_lock()	#request_id保护锁
		self.order_ref = 1
		self.order_lock = thread.allocate_lock()	#order_ref保护锁
		
		self.initialized = False
		self.front_id = None
		self.session_id = None
		self.scur_day = int(time.strftime('%Y%m%d'))
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
		#初始化日志接口
		initLoggingBasic()
			
		self.logger = logging.getLogger('Td')
		
		#初始化CTP交易接口
		traderSpi = CtpTraderApi(self.broker_id, self.investor_id, self.passwd, self)
		traderSpi.Create("TraderAgent")
		traderSpi.RegisterFront(self.server_port)
		traderSpi.Init()
		self.trader = traderSpi
		
		#等待确认API已正确登录
		waitLoggedSeconds = 10	#最长等待时间
		while waitLoggedSeconds > 0:
			time.sleep(1)
			if self.trader.is_logged:
				break
			
			waitLoggedSeconds -= 1
			
		if self.trader.is_logged == False:
			return False
		
		#预留时间给API接受完历史报单
		time.sleep(2)
		#print u'代理初始化完成'
		self.initialized = True
		
		return True
		
	def initialize (self):
		while self.isSettlementInfoConfirmed == False:
			time.sleep(1)
		
	def login_success (self,frontID, sessionID, max_order_ref):
		#print u'FrondId %s, SessionID %s, OrderRef %s' % (frontID, sessionID, max_order_ref)
		self.front_id = frontID
		self.session_id = sessionID
		self.order_ref = int(max_order_ref)
	
	def inc_request_id (self):
		self.request_lock.acquire()
		self.request_id += 1
		self.request_lock.release()
		return self.request_id
	
	#本地报单引用（数）维护
	def inc_order_ref(self):
		self.order_lock.acquire()
		self.order_ref += 1
		self.order_lock.release()
		return self.order_ref
		
	#开仓	
	def open_position (self, instrument, direction, price, volume):
		order_ref = self.inc_order_ref()
		self.trader.open_position(instrument, direction, order_ref, price, volume)
		return order_ref
		
	#平仓	
	def close_position (self, instrument, direction, price, volume, cos_flag=ApiStruct.OF_Close):
		order_ref = self.inc_order_ref()
		self.trader.close_position(instrument, direction, order_ref, price, volume, cos_flag)
		return order_ref
	
	#报单(状态)响应：CTP报单通知
	def rtn_order (self, order):
		#只有在初始化完成并接受完历史报单后才开始工作
		if self.initialized == False:
			return
		
		#接收报单状态，并更新在报单映射中
		self.orderMap.addElement(order.OrderRef, order)
		
	#成交响应：CTP成交通知
	def rtn_trade (self, trader):
		#只有在初始化完成并接受完历史报单后才开始工作
		if self.initialized == False:
			return
		
		#报单成交，从报单映射中删除
		self.orderMap.delElement(trader.OrderRef)
		
	#是否报单出错
	def is_err_order (self, 
		order_ref	#本地报单编号记录
		):
		#稍做睡眠以保证在判断前能正确接受到CTP服务器端的响应
		time.sleep(0.5)
		order = str(order_ref)
		return self.errOrderMap.isElementExisted(order)
		
	#返回报单是否成功
	def is_order_success (self, 
		order_ref	#本地报单编号记录
		):
		#稍做睡眠以保证在判断前能正确接受到CTP服务器端的响应
		#time.sleep(0.5)
		order = str(order_ref)
		return not self.orderMap.isElementExisted(order) and not self.errOrderMap.isElementExisted(order)
		
	#发起撤单申请
	def cancel_command(self, 
		instrument,	#合约
		order_ref	#本地报单编号记录
		):
		self.trader.cancel_command(instrument, order_ref)
		 
	#是否撤单成功
	def is_order_cancelled (self, 
		order_ref	#本地报单编号记录
		):
		#稍做睡眠以保证在判断前能正确接受到CTP服务器端的响应
		time.sleep(0.5)
		
		order = str(order_ref)
		'''
		错误报单映射中无记录证明成功撤单，如错误刻录存在则需检查是否已成交
		'''
		#print self.errOrderMap.elemDict
		#print self.orderMap.elemDict
		#print order, self.errOrderMap.isElementExisted(order)
		
		if self.errOrderMap.isElementExisted(order):
			if self.is_order_success(order):
				#报单已经成交，不能撤单，返回错误
				return False
			else:
				#撤单出错，返回异常
				return 'EXCEPT'
		
		else:
			#正常撤单，返回正确
			return True
		 
	#清除报单、错误映射中的记录
	def clear_ordermaps(self,
		order_ref	#本地报单编号记录
		):
		#print 'Clear orderMap and errOrderMap for %d' % order_ref
		order = str(order_ref)
		self.errOrderMap.delElement(order)
		self.orderMap.delElement(order)
		#print self.errOrderMap.elemDict
		#print self.orderMap.elemDict
	 
	#回调函数响应：插入报单出错
	def err_order_insert (self, pInputOrder):
		self.errOrderMap.addElement(pInputOrder.OrderRef, pInputOrder)
		pass
		
	#回调函数响应：CTP撤单错误通知
	def err_order_action (self, pInputOrderAction):
		self.errOrderMap.addElement(pInputOrderAction.OrderRef, pInputOrderAction)
			
	#查询报单
	def query_order (self, instrument, order_sys_id):
		self.trader.query_order(instrument, order_sys_id)
		
	#回调函数响应：CTP报单查询
	def rsp_qry_order (self, order):
		print order
		pass	
		