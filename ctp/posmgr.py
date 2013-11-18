#-*- coding:utf-8 -*-

'''
CTP持仓管理统一接口对象
'''

from time import sleep
from futures import ApiStruct

#CTP下单操作管理
class CtpPositionManager:
	timeWaitOrder = 10
	
	def __init__ (self, 
		mdAgent, 	#行情数据代理
		tdAgent		#交易服务器端代理
		):
		self.mdAgent = mdAgent
		self.tdAgent = tdAgent
		self.mdlocal = mdAgent.mdlocal
		
	#撤消下单
	def cancel_order (self, instrument, order_ref):
		try:
			self.tdAgent.cancel_command(instrument, order_ref)
		except:	
			print 'CtpPosition: cancel_order error'
			
	#开仓
	def open_position (self, instrument, direction, price, volume):
		try:
			order_ref = self.tdAgent.open_position(instrument, direction, price, volume)
			sleep(self.timeWaitOrder)
			
			ret = price
			while not self.tdAgent.is_order_success(order_ref):
				self.cancel_order(instrument, order_ref)
				price = self.mdlocal.getClose(instrument)
				order_ref = self.tdAgent.open_position(instrument, direction, price, volume)
				ret = price
				sleep(self.timeWaitOrder)
				
			return price
		except:
			print 'CtpPosition: open_position error'
			return None
		
		
	#开多
	def open_long_position (self, instrument, price, volume):
		return self.open_position(instrument, ApiStruct.D_Buy, price, volume)
	
	#开空
	def open_short_position (self, instrument, price, volume):
		return self.open_position(instrument, ApiStruct.D_Sell, price, volume)
		
	#平仓
	def close_position (self, instrument, direction, price, volume, cos_flag=ApiStruct.OF_Close):
		try:
			order_ref = self.tdAgent.close_position(instrument, direction, price, volume, cos_flag)
			sleep(self.timeWaitOrder)
			
			ret = price
			while not self.tdAgent.is_order_success(order_ref):
				self.cancel_order(instrument, order_ref)
				price = self.mdlocal.getClose(instrument)
				order_ref = self.tdAgent.close_position(instrument, direction, price, volume)
				ret = price
				sleep(self.timeWaitOrder)
				
			return price
		except:
			print 'CtpPosition: close_position error'
			return None
		
	#平多
	def close_long_position (self, instrument, price, volume):
		return self.close_position(instrument, ApiStruct.D_Sell, price, volume)
	
	#平空
	def close_short_position (self, instrument, price, volume):
		return self.close_position(instrument, ApiStruct.D_Buy, price, volume)
		