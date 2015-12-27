#! /usr/bin/python
#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start:  Wed Oct 28 19:21:03 2015

核心系统配置读写接口
"""

import sys
sys.path.append('..')

from misc.genconfig import *

# 并行模拟交易配置
class EmulationConfig (GenConfig):
	def __init__ (self, 
		cfgFile,	#配置文件
		):
		GenConfig.__init__(self, cfgFile)
		self.cfgFile = cfgFile
		self.defaultSec = 'EMULATION'	#默认配置段

	def getContracts (self):
		return self.getSecOption(self.defaultSec, 'contracts')	
	
	def getStartTime (self):
		return self.getSecOption(self.defaultSec, 'start_time')
	
	def getEndTime (self):
		return self.getSecOption(self.defaultSec, 'end_time')
	
	def getExpireDates (self):
		return self.getSecOption(self.defaultSec, 'expire_dates')
	
	def getContractAddMaxAllowed (self):
		return self.getSecOption(self.defaultSec, 'contract_add_max_allowed')
	
	def getContractVolumeAdd (self):
		return self.getSecOption(self.defaultSec, 'contract_volume_add')
	
	def getContractMultiplier (self):
		return self.getSecOption(self.defaultSec, 'contract_multiplier')
	
	def getContractTriggerLevel (self):
		return self.getSecOption(self.defaultSec, 'contract_trigger_level')
	
	def getParallelLevel (self):
		return self.getSecOption(self.defaultSec, 'parallel_level')
	
	def getParallelAddMaxAllowed (self):
		return self.getSecOption(self.defaultSec, 'parallel_add_max_allowed')

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
