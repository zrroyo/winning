#! /usr/bin/python
#-*- coding:utf-8 -*-

'''
Futures配置文件读取接口.
	zhengwang.ruan@gmail.com
'''

import sys
sys.path.append('..')

from misc.genconfig import GenConfig

class FutureConfig(GenConfig):
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
		
		
if __name__ == '__main__':
	futCfg = FutureConfig('../config/futures.ini')
	print futCfg.getInstruments('m')
	print futCfg.getStrategy('m')
	print futCfg.getAllowedPos('m')
	print futCfg.getMaxAddPos('m')
	print futCfg.getMinPos('m')
	print futCfg.getMinPosIntv('m')
	print futCfg.getPriceUnit('m')
	print futCfg.getStartDate('m')
	print futCfg.getTimeCtpOn('m')
	print futCfg.getNeedConfirm('m')
