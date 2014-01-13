#! /usr/bin/python
#-*- coding:utf-8 -*-

'''
加仓管理模块(Add-Position Manangement Module)
'''

#加仓类
class AddPosition:
	def __init__ (self,
		price,		#价格
		time = None,	#时间
		):
		self.price = price
		self.time = time
		
#仓位管理接口
class PositionMananger:
	
	__posStack = []	#持仓栈

	def __init__ (self,
		maxAddPos,	#最大可加仓数
		):
		self.maxAddPos = maxAddPos
		
	#当前已加仓数
	def numPositions (self):
		return len(self.__posStack)
		
	#压（加）仓
	def pushPosition (self,
		price,		#价格
		time = None,	#时间
		):
		if self.numPositions() >= self.maxAddPos:
			return None
			
		addPos = AddPosition(price, time)
		self.__posStack.append(addPos)
		
		return price
		
	#减仓
	def popPosition (self):
		if self.numPositions() == 0:
			return None
		
		return self.__posStack.pop()
		
def doTest():
	posMgr = PositionMananger(3)
		
	time = '2014-1-13'
	print posMgr.pushPosition(3666, time)
	print posMgr.pushPosition(3677, time)
	print posMgr.pushPosition(3688, time)
	print posMgr.pushPosition(3699, time)
	
	while posMgr.numPositions():
		pos = posMgr.popPosition()
		print pos.price, pos.time
		
if __name__ == '__main__':
	doTest()
	