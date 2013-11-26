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
		strategy=None	#交易策略对象（实例）
		):
		self.mdAgent = mdAgent
		self.tdAgent = tdAgent
		self.mdlocal = mdAgent.mdlocal
		'''
		有的时候需要访问在被调用策略里的一些接口、变量。
		'''
		self.strategy = strategy
		
	#撤消下单
	def cancel_order (self, instrument, order_ref):
		try:
			self.tdAgent.cancel_command(instrument, order_ref)
		except:	
			self.log('CtpPosition: cancel_order error')
			
	#开仓
	def open_position (self, instrument, direction, price, volume):
		#print u'open_position'
		try:
			order_ref = self.tdAgent.open_position(instrument, direction, price, volume)
			sleep(self.timeWaitOrder)
			
			#print order_ref, self.tdAgent.is_order_success(order_ref)
			#print self.tdAgent.orderMap.elemDict
			ret = price
			while not self.tdAgent.is_order_success(order_ref):
				#如果开仓不成功，刚重新获取市场价并报单重开
				self.cancel_order(instrument, order_ref)
				price = self.mdlocal.getClose(instrument)
				self.log('Cancel order %d, new price %d' % (order_ref, price))
				order_ref = self.tdAgent.open_position(instrument, direction, price, volume)
				ret = price
				sleep(self.timeWaitOrder)
				
			return price
		except:
			self.log('CtpPosition: open_position error')
			return None
		
		
	#开多
	def open_long_position (self, instrument, price, volume):
		self.log('Opening [long] position  %g, %d' % (price, volume))
		return self.open_position(instrument, D_Buy, price, volume)
	
	#开空
	def open_short_position (self, instrument, price, volume):
		self.log('Opening [short] position  %g, %d' % (price, volume))
		return self.open_position(instrument, D_Sell, price, volume)
		
	#平仓
	def close_position (self, instrument, direction, price, volume, cos_flag=OF_Close):
		try:
			order_ref = self.tdAgent.close_position(instrument, direction, price, volume, cos_flag)
			sleep(self.timeWaitOrder)
			
			ret = price
			while not self.tdAgent.is_order_success(order_ref):
				#如果平仓不成功，刚重新获取市场价并报单重平
				self.cancel_order(instrument, order_ref)
				price = self.mdlocal.getClose(instrument)
				self.log('Cancel order %d, new price %d' % (order_ref, price))
				order_ref = self.tdAgent.close_position(instrument, direction, price, volume, cos_flag)
				ret = price
				sleep(self.timeWaitOrder)
				
			return price
		except:
			self.log('CtpPosition: close_position error')
			return None
		
	#平多
	def close_long_position (self, instrument, price, volume, cos_flag=OF_Close):
		self.log('Closing [long] position %g, %d' % (price, volume))
		return self.close_position(instrument, D_Sell, price, volume, cos_flag)
	
	#平空
	def close_short_position (self, instrument, price, volume, cos_flag=OF_Close):
		self.log('Closing [short] position  %g, %d' % (price, volume))
		return self.close_position(instrument, D_Buy, price, volume, cos_flag)
		
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
		