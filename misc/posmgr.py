#! /usr/bin/python
#-*- coding:utf-8 -*-

"""
加仓管理模块(Add-Position Manangement Module)
"""

import sys
sys.path.append("..")

from misc.debug import *

# 加仓类
class Position:
	def __init__ (self,
		price,		#价格
		time,		#时间
		volume,		#开仓手数
		direction,	#方向
		):
		self.price = price
		self.time = time
		self.volume = volume
		self.direction = direction
		
# 仓位管理接口
class PositionManager:
	def __init__ (self,
		maxAddPos,	#最大可加仓数
		prompt = None,	#调试提示符
		debug = False,	#是否调试
		):
		self.maxAddPos = maxAddPos
		# 持仓栈
		self.__posStack = []
		prompt =  "PositionManager" if not prompt else "PositionManager:%s" % prompt
		self.debug = Debug(prompt, debug)	#调试接口
		
	# 当前仓位
	def numPositions (self):
		return len(self.__posStack)
		
	# 加仓
	def pushPosition (self,
		time,			#时间
		price,			#价格
		volume = 1,		#数量
		direction = None,	#方向
		):
		if self.numPositions() >= self.maxAddPos:
			return False
			
		addPos = Position(price, time, volume, direction)
		self.__posStack.append(addPos)
		self.debug.dbg("current %s" % self.numPositions())
		return True
		
	# 减仓
	def popPosition (self,
		num = None,	#仓位标号
		):
		try:
			# 标号为None则返回末位仓
			if not num:
				return self.__posStack.pop()

			# 否则返回指定仓
			pos = self.__posStack.pop(num - 1)
			self.debug.dbg("current %s" % self.numPositions())
			return pos
		except IndexError, e:
			self.debug.error("getPosition: num %s, current %s\n %s" % (
							num, self.numPositions(), e))
			return None

	# 对所有仓位指定字段求和
	def valueSum (self,
		value = 'price',	#指定字段
		):
		poses = self.numPositions()
		if poses == 0:
			return 0
		elif poses == 1:
			ret = self.getPosition(1).price
			if value == 'volume':
				ret = self.getPosition(1).volume
			return ret

		# 仓位大于1
		# self.debug.dbg("poses: %s" % self.__posStack)
		_funcSum = lambda x, y : Position(x.price + y.price, None, 0, None)
		if value == 'volume':
			_funcSum = lambda x, y : Position(0.0, None, x.volume + y.volume, None)

		ret = reduce(_funcSum, self.__posStack)
		return ret.price

	# 返回第num个仓位，num从１开始记
	def getPosition (self, 
		num,	#仓位标号
		):
		try:
			return self.__posStack[num - 1]
		except IndexError, e:
			self.debug.error("getPosition: num %s, current %s\n %s" % (
							num, self.numPositions(), e))
			return None
		
	# 清空持仓
	def empty (self):
		self.__posStack = []
		
# 测试
def doTest():
	posMgr = PositionManager(3)
		
	time = '2014-1-13'
	print posMgr.pushPosition(time, 3666, 2)
	print posMgr.pushPosition(time, 3677, direction = 0)
	print posMgr.pushPosition(time, 3688, 3)
	print posMgr.pushPosition(time, 3699)
	print posMgr.getPosition(3).price
	print posMgr.getPosition(4)
	
	pos = posMgr.popPosition(1)
	print pos.price, pos.time, pos.volume, pos.direction

	while posMgr.numPositions():
		pos = posMgr.popPosition()
		print pos.price, pos.time, pos.volume, pos.direction
		
	pos = posMgr.popPosition()
	
	# 测试结果
	'''
	3666
	3677
	3688
	None
	3688
	ERR: PositionManager: getPosition: num [3] overflow [3]!
	None
	3666 2014-1-13 2 None
	3688 2014-1-13 3 None
	3677 2014-1-13 1 0
	ERR: PositionManager: popPosition: num [None] overflow [0]!
	'''
	
if __name__ == '__main__':
	doTest()
	