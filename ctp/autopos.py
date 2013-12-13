#-*- coding:utf-8 -*-

'''
CTP加强版持仓管理统一接口
'''

from time import sleep
from futures import ApiStruct

##开平标志(OffsetFlag)全局定义
OF_Open 		= ApiStruct.OF_Open
OF_Close 		= ApiStruct.OF_Close
OF_ForceClose 		= ApiStruct.OF_ForceClose
OF_CloseToday 		= ApiStruct.OF_CloseToday
OF_CloseYesterday 	= ApiStruct.OF_CloseYesterday
OF_ForceOff 		= ApiStruct.OF_ForceOff
OF_LocalForceClose 	= ApiStruct.OF_LocalForceClose

#买卖方向(Direction)全局定义
D_Buy 	= ApiStruct.D_Buy
D_Sell	= ApiStruct.D_Sell

#CTP下单操作管理
class CtpAutoPosition:
	'''
	加强性能：开平仓操作都会以指定价报单，但如果默认时限内没成交，刚会尝试以市场价成交，直到成功。
	'''
	timeWaitOrder = 10	#等待某操作完成时限(默认值)
	
	def __init__ (self, 
		mdAgent,	#行情数据代理
		tdAgent,	#交易服务器端代理
		strategy=None,	#交易策略对象（实例）
		optPriceLimit=2	#决定合理价时的次数阈值
		):
		self.mdAgent = mdAgent
		self.tdAgent = tdAgent
		self.mdlocal = mdAgent.mdlocal
		'''
		有的时候需要访问在被调用策略里的一些接口、变量。
		'''
		self.strategy = strategy
		self.optPriceLimit = optPriceLimit
		
	#撤消下单
	def cancel_order (self, instrument, order_ref):
		try:
			self.tdAgent.cancel_command(instrument, order_ref)
		except:	
			self.log('CtpPosition: cancel_order error')
			
	#得到合理的买入价
	def __getReasonableBuyPrice (self, instrument, count):
		if count < self.optPriceLimit:
			return self.mdlocal.getBidPrice1(instrument)
		elif count < self.optPriceLimit*2:
			return self.mdlocal.getClose(instrument)
		else:
			return self.mdlocal.getAskPrice1(instrument)
		
	#得到合理的卖出价
	def __getReasonableSellPrice (self, instrument, count):
		if count < self.optPriceLimit:
			return self.mdlocal.getAskPrice1(instrument)
		elif count < self.optPriceLimit*2:
			return self.mdlocal.getClose(instrument)
		else:
			return self.mdlocal.getBidPrice1(instrument)
			
	#开多
	def open_long_position (self, instrument, buyPrice, volume):
		count = 0
		price = self.__getReasonableBuyPrice(instrument, count)
		self.log('Opening [long] position, trigger %g, buy %g, %d' % (buyPrice, price, volume))
		
		try:
			while 1:
				count += 1
				order_ref = self.tdAgent.open_position(instrument, D_Buy, price, volume)
				sleep(self.timeWaitOrder)
				
				if self.tdAgent.is_order_success(order_ref):
					break
				
				#如果开仓不成功，刚重新获取合理价并报单重开
				self.cancel_order(instrument, order_ref)
				price = self.__getReasonableBuyPrice(instrument, count)
				self.log('Cancel order %d, new price %d, count %d' % (order_ref, price, count))
					
			return price
		except:
			self.log('CtpPosition: open_long_position error')
			return None
			
	#开空
	def open_short_position (self, instrument, sellPrice, volume):
		count = 0
		price = self.__getReasonableSellPrice(instrument, count)
		self.log('Opening [short] position, trigger %g, sell %g, %d' % (sellPrice, price, volume))
		
		try:
			while 1:
				count += 1
				order_ref = self.tdAgent.open_position(instrument, D_Sell, price, volume)
				sleep(self.timeWaitOrder)
				
				if self.tdAgent.is_order_success(order_ref):
					break
					
				#如果开仓不成功，刚重新获取合理价并报单重开
				self.cancel_order(instrument, order_ref)
				price = self.__getReasonableSellPrice(instrument, count)
				self.log('Cancel order %d, new price %d, count %d' % (order_ref, price, count))
					
			return price
		except:
			self.log('CtpPosition: open_short_position error')
			return None
			
	#平多
	def close_long_position (self, instrument, sellPrice, volume, cos_flag=OF_CloseYesterday):
		count = 0
		price = self.__getReasonableSellPrice(instrument, count)
		self.log('Closing [long] position, trigger %g, sell %g, %d' % (sellPrice, price, volume))
		
		try:
			while 1:
				count += 1
				order_ref = self.close_position(instrument, D_Sell, price, volume, cos_flag)
				sleep(self.timeWaitOrder)
				
				if self.tdAgent.is_order_success(order_ref):
					break
					
				#如果开仓不成功，刚重新获取合理价并报单重开
				self.cancel_order(instrument, order_ref)
				price = self.__getReasonableSellPrice(instrument, count)
				self.log('Cancel order %d, new price %d, count %d' % (order_ref, price, count))
					
			return price
		except:
			self.log('CtpPosition: close_long_position error')
			return None
		
	#平空
	def close_short_position (self, instrument, buyPrice, volume, cos_flag=OF_CloseYesterday):
		count = 0
		price = self.__getReasonableBuyPrice(instrument, count)
		self.log('Closing [short] position, trigger %g, sell %g, %d' % (buyPrice, price, volume))
		
		try:
			while 1:
				count += 1
				order_ref = self.close_position(instrument, D_Buy, price, volume, cos_flag)
				sleep(self.timeWaitOrder)
				
				if self.tdAgent.is_order_success(order_ref):
					break
					
				#如果开仓不成功，刚重新获取合理价并报单重开
				self.cancel_order(instrument, order_ref)
				price = self.__getReasonableBuyPrice(instrument, count)
				self.log('Cancel order %d, new price %d, count %d' % (order_ref, price, count))
					
			return price
		except:
			self.log('CtpPosition: close_short_position error')
			return None
		
	#日志（输出）统一接口
	def log (self, logMsg, *args):
		'''
		运用被调用策略的日志输出接口统一输出，避免混乱。
		'''
		logs = logMsg % (args)
		if self.strategy is not None:
			#print logMsg, args
			self.strategy.log(logs)
		else:
			print logs
		