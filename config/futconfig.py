#! /usr/bin/python

'''
Futures Config Class.
	
	zhengwang.ruan@gmail.com
'''

from genconfig import GenConfig

class FutureConfig(GenConfig):
	def getStrategy (self, section):
		return self.getSecOption(section, 'strategy')
	
	def getMaxAddPos(self, section):
		return self.getSecOption(section, 'max_add_pos')
		
	def getMinPos (self, section):
		return self.getSecOption(section, 'min_pos')
	
	def getMinPosIntv (self, section):
		return self.getSecOption(section, 'min_pos_intv')
		
	def getPriceUnit (self, section):
		return self.getSecOption(section, 'price_uint')
		
	def getMode (self, section):
		return self.getSecOption(section, 'mode')
		
	def getStartDate (self, section):
		return self.getSecOption(section, 'start_date')
		
	def getNeedConfirm (self, section):
		return self.getSecOption(section, 'need_confirm')
		
		
#if __name__ == '__main__':
	#futCfg = FutureConfig('futures.ini')
	#print futCfg.getStrategy('m1401')
	#print futCfg.getMaxAddPos('m1401')
	#print futCfg.getMinPos('m1401')
	#print futCfg.getMinPosIntv('m1401')
	#print futCfg.getPriceUnit('m1401')
	#print futCfg.getMode('m1401')
	#print futCfg.getStartDate('m1401')
	#print futCfg.getNeedConfirm('m1401')
