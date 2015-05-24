#! /usr/bin/python
#-*- coding:utf-8 -*-

'''
加仓管理模块(Add-Position Manangement Module)
'''

import sys
sys.path.append("..")

from misc.debug import *

#加仓类
class AddPosition:
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
		
#仓位管理接口
class PositionMananger:
	
	__posStack = []	#持仓栈

	def __init__ (self,
		maxAddPos,	#最大可加仓数
		debug = False,	#是否调试
		):
		self.maxAddPos = maxAddPos
		self.debug = Debug('PositionMananger', debug)	#调试接口
		
	#当前已加仓数
	def numPositions (self):
		return len(self.__posStack)
		
	#压（加）仓
	def pushPosition (self,
		time,			#时间
		price,			#价格
		volume = 1,		#数量
		direction = None,	#方向
		):
		if self.numPositions() >= self.maxAddPos:
			return None
			
		addPos = AddPosition(price, time, volume, direction)
		self.__posStack.append(addPos)
		
		return price
		
	#减仓
	def popPosition (self,
		num = None,	#仓位标号
		):
		try:
			#标号为None则返回末位仓
			if not num:
				return self.__posStack.pop()
			
			#否则返回指定仓
			num -= 1
			pos = self.__posStack[num]
			del self.__posStack[num]
			return pos
		except:
			self.debug.error("popPosition: num [%s] overflow [%s]!" % (
							num, self.numPositions()))
			return None
		
	#返回第num个仓位，num从１开始记
	def getPosition (self, 
		num,	#仓位标号
		):
		try:
			num -= 1
			return self.__posStack[num]
		except:
			self.debug.error("getPosition: num [%s] overflow [%s]!" % (
							num, self.numPositions()))
			return None
		
	#清空持仓
	def empty (self):
		self.__posStack = []
		
#测试
def doTest():
	posMgr = PositionMananger(3)
		
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
	
	#测试结果
	'''
	3666
	3677
	3688
	None
	3688
	ERR: PositionMananger: getPosition: num [3] overflow [3]!
	None
	3666 2014-1-13 2 None
	3688 2014-1-13 3 None
	3677 2014-1-13 1 0
	ERR: PositionMananger: popPosition: num [None] overflow [0]!
	'''
	
if __name__ == '__main__':
	doTest()
	