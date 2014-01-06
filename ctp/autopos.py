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
	def cancelOrder (self, 
		instrument,	#合约
		order_ref	#本地报单序号
		):
		try:
			self.tdAgent.cancel_command(instrument, order_ref)
		except:	
			self.log('CtpAutoPosition: cancelOrder error')
			
	#得到合理的买入价
	def __getReasonableBuyPrice (self, 
		instrument,	#合约
		count		#累计判断次数
		):
		if count < self.optPriceLimit:
			return self.mdlocal.getBidPrice1(instrument)
		elif count < self.optPriceLimit*2:
			return self.mdlocal.getClose(instrument)
		else:
			return self.mdlocal.getAskPrice1(instrument)
		
	#得到合理的卖出价
	def __getReasonableSellPrice (self, 
		instrument,	#合约
		count		#累计判断次数
		):
		if count < self.optPriceLimit:
			return self.mdlocal.getAskPrice1(instrument)
		elif count < self.optPriceLimit*2:
			return self.mdlocal.getClose(instrument)
		else:
			return self.mdlocal.getBidPrice1(instrument)
			
	#停止执行
	def halt(self):
		while 1:
			#try:
				#sleep(5)
			#except:
				#self.log('CtpAutoPosition: Received cxception but halting...')
			sleep(5)
		
	#开多
	def openLongPosition (self, 
		instrument,	#合约
		buyPrice,	#买入价
		volume		#手数
		):
		count = 0
		price = self.__getReasonableBuyPrice(instrument, count)
		self.log('Opening [long] position, trigger %g, buy %g, %d' % (buyPrice, price, volume))
		
		try:
			while 1:
				count += 1
				order_ref = self.tdAgent.open_position(instrument, D_Buy, price, volume)
				if self.tdAgent.is_err_order(order_ref):
					self.log('openLongPosition: Failed to insert order, halting...')
					self.halt()
				
				sleep(self.timeWaitOrder)
					
				if self.tdAgent.is_order_success(order_ref):
					break
				
				#如果开仓不成功，刚重新获取合理价并报单重开
				self.cancelOrder(instrument, order_ref)
				cancelled = self.tdAgent.is_order_cancelled(order_ref)
				if cancelled == False:
					#报单已经成交
					break
				elif cancelled == 'EXCEPT':
					self.log('openLongPosition: Failed to cancel order, halting...')
					self.halt()
				
				#成功撤单，清除在报单状态映射中的记录
				self.tdAgent.clear_ordermaps(order_ref)
				
				price = self.__getReasonableBuyPrice(instrument, count)
				self.log('Cancel order %d, new price %d, count %d' % (order_ref, price, count))
					
			return price
		except:
			self.log('CtpAutoPosition: openLongPosition error')
			return None
			
	#开空
	def openShortPosition (self, 
		instrument,	#合约
		sellPrice,	#卖出价
		volume		#手数
		):
		count = 0
		price = self.__getReasonableSellPrice(instrument, count)
		self.log('Opening [short] position, trigger %g, sell %g, %d' % (sellPrice, price, volume))
		
		try:
			while 1:
				count += 1
				order_ref = self.tdAgent.open_position(instrument, D_Sell, price, volume)
				if self.tdAgent.is_err_order(order_ref):
					self.log('openShortPosition: Failed to insert order, halting...')
					self.halt()
				
				sleep(self.timeWaitOrder)
					
				if self.tdAgent.is_order_success(order_ref):
					break
					
				#如果开仓不成功，刚重新获取合理价并报单重开
				self.cancelOrder(instrument, order_ref)
				cancelled = self.tdAgent.is_order_cancelled(order_ref)
				if cancelled == False:
					#报单已经成交
					break
				elif cancelled == 'EXCEPT':
					self.log('openShortPosition: Failed to cancel order, halting...')
					self.halt()
					
				#成功撤单，清除在报单状态映射中的记录
				self.tdAgent.clear_ordermaps(order_ref)
					
				price = self.__getReasonableSellPrice(instrument, count)
				self.log('Cancel order %d, new price %d, count %d' % (order_ref, price, count))
					
			return price
		except:
			self.log('CtpAutoPosition: openShortPosition error')
			return None
			
	#平多
	def closeLongPosition (self, 
		instrument,	#合约
		sellPrice,	#卖出价
		volume,		#手数
		cos_flag=OF_Close	#平仓标志，默认为平前仓
		):
		count = 0
		price = self.__getReasonableSellPrice(instrument, count)
		self.log('Closing [long] position, trigger %g, sell %g, %d' % (sellPrice, price, volume))
		
		try:
			while 1:
				count += 1
				order_ref = self.tdAgent.close_position(instrument, D_Sell, price, volume, cos_flag)
				if self.tdAgent.is_err_order(order_ref):
					self.log('closeLongPosition: Failed to insert order, halting...')
					self.halt()
				
				sleep(self.timeWaitOrder)
						
				if self.tdAgent.is_order_success(order_ref):
					break
					
				#如果开仓不成功，刚重新获取合理价并报单重开
				self.cancelOrder(instrument, order_ref)
				cancelled = self.tdAgent.is_order_cancelled(order_ref)
				if cancelled == False:
					#报单已经成交
					break
				elif cancelled == 'EXCEPT':
					self.log('closeLongPosition: Failed to cancel order, halting...')
					self.halt()
				
				#成功撤单，清除在报单状态映射中的记录
				self.tdAgent.clear_ordermaps(order_ref)
				
				price = self.__getReasonableSellPrice(instrument, count)
				self.log('Cancel order %d, new price %d, count %d' % (order_ref, price, count))
					
			return price
		except:
			self.log('CtpAutoPosition: closeLongPosition error')
			return None
		
	#平空
	def closeShortPosition (self, 
		instrument,	#合约
		buyPrice,	#买入价
		volume,		#手数
		cos_flag=OF_Close	#平仓标志，默认为平前仓
		):
		count = 0
		price = self.__getReasonableBuyPrice(instrument, count)
		self.log('Closing [short] position, trigger %g, sell %g, %d' % (buyPrice, price, volume))
		
		try:
			while 1:
				count += 1
				order_ref = self.tdAgent.close_position(instrument, D_Buy, price, volume, cos_flag)
				if self.tdAgent.is_err_order(order_ref):
					self.log('closeShortPosition: Failed to insert order, halting...')
					self.halt()
				
				sleep(self.timeWaitOrder)
						
				if self.tdAgent.is_order_success(order_ref):
					break
					
				#如果开仓不成功，刚重新获取合理价并报单重开
				self.cancelOrder(instrument, order_ref)
				cancelled = self.tdAgent.is_order_cancelled(order_ref)
				if cancelled == False:
					#报单已经成交
					break
				elif cancelled == 'EXCEPT':
					self.log('closeShortPosition: Failed to cancel order, halting...')
					self.halt()
				
				#成功撤单，清除在报单状态映射中的记录
				self.tdAgent.clear_ordermaps(order_ref)
				
				price = self.__getReasonableBuyPrice(instrument, count)
				self.log('Cancel order %d, new price %d, count %d' % (order_ref, price, count))
					
			return price
		except:
			self.log('CtpAutoPosition: closeShortPosition error')
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
		