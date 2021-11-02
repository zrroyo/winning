#! /usr/bin/env python
#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start:  Wed Oct 28 19:21:03 2015

核心系统配置读写接口
"""

import sys
sys.path.append('..')

from misc.genconfig import *


class EmulationConfig (GenConfig):
	def __init__ (self, cfgFile):
		"""
		并行模拟交易配置
		:param cfgFile: 配置文件
		"""
		GenConfig.__init__(self, cfgFile)
		self.cfgFile = cfgFile
		self.defaultSec = 'EMULATION'	#默认配置段

	def getDatabase (self):
		return self.getSecOption(self.defaultSec, 'database')

	def getContracts (self):
		return self.getSecOption(self.defaultSec, 'contracts')	
	
	def getStartTime (self):
		return self.getSecOption(self.defaultSec, 'start_time')
	
	def getEndTime (self):
		return self.getSecOption(self.defaultSec, 'end_time')
	
	def getExpireDates (self):
		return self.getSecOption(self.defaultSec, 'expire_dates')

	def getParallelLevel (self):
		return self.getSecOption(self.defaultSec, 'parallel_level')
	
	def getParallelAddMaxAllowed (self):
		return self.getSecOption(self.defaultSec, 'parallel_add_max_allowed')

	def getParallelCapital (self):
		return self.getSecOption(self.defaultSec, 'parallel_capital')


class AttributeConfig (GenConfig):
	"""Futures交易属性配置"""
	def __init__ (self, cfgFile):
		"""
		:param cfgFile: 配置文件
		"""
		GenConfig.__init__(self, cfgFile)
		self.cfgFile = cfgFile
		self.defaultSec = 'Attributes'  # 默认配置段

	def getContractAddMaxAllowed(self):
		return self.getSecOption(self.defaultSec, 'contract_add_max_allowed')

	def getContractVolumeAdd(self):
		return self.getSecOption(self.defaultSec, 'contract_volume_add')

	def getContractTriggerLevel(self):
		return self.getSecOption(self.defaultSec, 'contract_trigger_level')

	def getPosThresholds(self):
		return self.getSecOption(self.defaultSec, 'pos_thresholds')


class ContractDescConfig (GenConfig):
	def __init__ (self, cfgFile):
		"""
		合约描述配置
		:param cfgFile: 配置文件
		"""
		GenConfig.__init__(self, cfgFile)
		self.cfgFile = cfgFile

	def getDatabase (self, contract):
		return self.getSecOption(contract, 'database')

	def getDaykTable (self, contract):
		return self.getSecOption(contract, 'dayk_table')

	def getMinkTable (self, contract):
		return self.getSecOption(contract, 'mink_table')

	def getDataLevel (self, contract):
		"""
		返回数据级别类型。days代表日K级数据，minutes为分钟级数据。
		"""
		return self.getSecOption(contract, 'data_level')

	def getContractStart (self, contract):
		return self.getSecOption(contract, 'contract_start')

	def getContractEnd (self, contract):
		return self.getSecOption(contract, 'contract_end')

	def getMultiplier (self, contract):
		return self.getSecOption(contract, 'multiplier')

	def getMarginRatio (self, contract):
		return self.getSecOption(contract, 'margin_ratio')

# 测试
def doTest ():
	emulConfig = EmulationConfig('../config/emul_p')
	print emulConfig.getContracts()
	print emulConfig.getStartTime()
	print emulConfig.getEndTime()
	print emulConfig.getExpireDates()
	print emulConfig.getContractAddMaxAllowed()
	print emulConfig.getContractVolumeAdd()
	print emulConfig.getContractMultiplier()
	print emulConfig.getContractTriggerLevel()
	print emulConfig.getParallelLevel()
	print emulConfig.getParallelAddMaxAllowed()

if __name__ == '__main__':
	doTest()
