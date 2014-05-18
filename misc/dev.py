#-*- coding:utf-8 -*-

'''

'''

from debug import *

#
class DevStat:
	
	highest = []	#
	highCount = 0	#
	lowest = []	#
	lowCount = 0	#
	
	def __init__ (self,
		debug = False,		#调试模式
		):
		self.debug = Debug('DevStat', debug)	#调试接口
		
	#
	def statHighestLowest (self, 
		high,	#
		low,	#
		):
		self.highest.append(high)
		self.highCount += 1
		self.lowest.append(high)
		self.lowCount += 1
		self.debug.dbg('High %s highCount %s, Low %s lowCount %s' % 
				(high, self.highCount, low, self.lowCount))
	