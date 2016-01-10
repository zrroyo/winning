#! /usr/bin/python
#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2015年 11月 21日 星期六 17:36:12 CST

模拟交易、回归测试核心模块
"""

import sys
sys.path.append("..")
import threading
import time

from misc.debug import Debug
from corecfg import EmulationConfig
from parallel import ParallelCore

from strategy.test_dev import TestFuture

#
DEF_SYNC_INTERVAL = 30
#
DEF_EMUL_CONFIG_DIR = "config"

#模拟交易、仿真核心
class Emulation:
	def __init__ (self,
		cfg,		#
		dumpName,	#统计信息Dump名
		debug = False,	#是否调试
		):
		self.debug = Debug('PositionAllocator', debug)	#调试接口
		self.emuCfg = EmulationConfig(cfg)	#
		#
		self.paraCore = ParallelCore(startTick = self.emuCfg.getStartTime(),
						interval = DEF_SYNC_INTERVAL,
						maxVolume = self.emuCfg.getParallelAddMaxAllowed(),
						parallelLevel = self.emuCfg.getParallelLevel(),
						dumpName = dumpName,
						debug = debug,
						)

	#
	def __setupContractProcess (self,
		contract,	#
		):
		strategy = TestFuture(contract = contract,
				      table = contract,
				      database = self.emuCfg.getDatabase(),
				      debug = True)

		strategy.setAttrs(maxPosAllowed = self.emuCfg.getContractAddMaxAllowed(),
				numPosToAdd = self.emuCfg.getContractVolumeAdd(),
				priceVariation = self.emuCfg.getContractTriggerLevel(),
				multiplier = self.emuCfg.getContractMultiplier(),
				dumpName = contract,
				paraCore = self.paraCore)

		#
		while not self.paraCore.allocManager(contract):
			time.sleep(0.5)

		thrContract = threading.Thread(target = threadContract, args = (strategy, ))
		thrContract.start()
		return thrContract

	#
	def start (self,
		startTick,	#
		):
		#
		thrPara = threading.Thread(target = threadParallelCore,
					   args = (self.paraCore, ))
		thrPara.start()

		#
		contracts = self.emuCfg.getContracts().split(',')
		for c in contracts:
			self.__setupContractProcess(c)

		#
		thrPara.join()


#
def threadParallelCore (
	paraCore,	#
	):
	paraCore.handleActions()

#
def threadContract(
	strategy,	#
	):
	#
	strategy.start()

# 测试
def doTest():
	global DEF_EMUL_CONFIG_DIR
	DEF_EMUL_CONFIG_DIR = "../config"

	testCfg = "%s/test_emul" % DEF_EMUL_CONFIG_DIR
	emul = Emulation(cfg = testCfg,
			 dumpName = "test_emul",
			 debug = True)
	emul.start()

if __name__ == '__main__':
	doTest()
