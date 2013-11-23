#! /usr/bin/python
#-*- coding:utf-8 -*-

'''
Futures配置文件读取接口.
	zhengwang.ruan@gmail.com
'''

import sys
sys.path.append('..')

from misc.genconfig import GenConfig

#交易（策略）配置文件读取接口
class TradingConfig(GenConfig):
	def getInstruments (self, section):
		return self.getSecOption(section, 'instruments')
		
	def getStrategy (self, section):
		return self.getSecOption(section, 'strategy')
		
	def getAllowedPos(self, section):
		return self.getSecOption(section, 'allowed_pos')
		
	def getMaxAddPos(self, section):
		return self.getSecOption(section, 'max_add_pos')
		
	def getMinPos (self, section):
		return self.getSecOption(section, 'min_pos')
	
	def getMinPosIntv (self, section):
		return self.getSecOption(section, 'min_pos_intv')
		
	def getPriceUnit (self, section):
		return self.getSecOption(section, 'price_uint')
		
	def getStartDate (self, section):
		return self.getSecOption(section, 'start_date')
		
	def getTimeCtpOn (self, section):
		return self.getSecOption(section, 'time_ctp_on')
		
	def getNeedConfirm (self, section):
		return self.getSecOption(section, 'need_confirm')
		
	def getEnabled (self, section):
		return self.getSecOption(section, 'enabled')
		
	def getDatabase (self, section):
		return self.getSecOption(section, 'database')
		
#CTP服务器端口配置文件读取接口
class CtpConfig(GenConfig):
	def getServer (self, section):
		return self.getSecOption(section, 'server')	
		
	def getPasswd (self, section):
		return self.getSecOption(section, 'passwd')
		
	def getInvestor (self, section):
		return self.getSecOption(section, 'investor')
		
	def getBrokerid (self, section):
		return self.getSecOption(section, 'broker_id')
		
		
if __name__ == '__main__':
	print u'测试TradingConfig接口：'
	tradeConfig = TradingConfig('../config/test.ini')
	print tradeConfig.getInstruments('m')
	print tradeConfig.getStrategy('m')
	print tradeConfig.getAllowedPos('m')
	print tradeConfig.getMaxAddPos('m')
	print tradeConfig.getMinPos('m')
	print tradeConfig.getMinPosIntv('m')
	print tradeConfig.getPriceUnit('m')
	print tradeConfig.getStartDate('m')
	print tradeConfig.getTimeCtpOn('m')
	print tradeConfig.getNeedConfirm('m')
	print tradeConfig.getEnabled('m')
	print tradeConfig.getDatabase('m')

	print u'\n测试CtpConfig接口：'
	ctpConfig = CtpConfig('../config/ctp.ini')
	print ctpConfig.getServer('MarketData')
	print ctpConfig.getPasswd('MarketData')
	print ctpConfig.getInvestor('MarketData')
	print ctpConfig.getBrokerid('MarketData')
	print ctpConfig.getServer('Trade')
	print ctpConfig.getPasswd('Trade')
	print ctpConfig.getInvestor('Trade')
	print ctpConfig.getBrokerid('Trade')
	