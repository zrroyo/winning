#-*- coding:utf-8 -*-

'''
元素映射（Elements Mapping）
'''

import copy

# Element Dict Map.
class ElementMap:
	def __init__ (self):
		self.elemDict = {}
		pass
	
	#添加一个元素
	def addElement (self, name, element):
		dp = copy.deepcopy(element)
		self.elemDict[name] = dp
	
	#删除一个元素
	def delElement (self, name):
		return self.elemDict.pop(name)
	
	#删除所有元素映射
	def delElementMap (self):
		self.elemDict.clear()
		
	#更新元素内容
	def updateElement (self, name, element):
		self.addElement(name, element)
	
	#获取元素、内容
	def getElement (self, name):
		return self.elemDict[name]
	
	#判断某个元素是否已经存在于映射中
	def isElementExisted (self, name):
		if name in self.elemDict.keys():
			return True
		else:
			return False
		