#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2015年 05月 22日 星期五 23:50:13 CST

期货合约（交易）属性模块
"""

#期货合约（交易）属性类
class Attribute:
	def __init__ (self,
		maxPosAllowed = None,	#最大允许持仓单位数
		numPosToAdd = None,	#每加仓单位所代表的手数
		priceVariation = None,	#触发加仓条件的价格差
		multiplier = None,	#合约乘数
		):
		self.maxPosAllowed = maxPosAllowed
		self.numPosToAdd = numPosToAdd
		self.priceVariation = priceVariation
		self.multiplier = multiplier
	
	#设置属性
	def set (self,
		maxPosAllowed,	#最大允许持仓单位数
		numPosToAdd,	#每加仓单位所代表的手数
		priceVariation,	#触发加仓条件的价格差
		multiplier,	#合约乘数
		):
		self.maxPosAllowed = maxPosAllowed
		self.numPosToAdd = numPosToAdd
		self.priceVariation = priceVariation
		self.multiplier = multiplier
	