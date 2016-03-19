#! /usr/bin/python
#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2015年 11月 21日 星期六 17:36:12 CST

模拟交易、回归测试核心模块
"""

import sys
sys.path.append("..")
import thread
import time

from misc.debug import Debug
from corecfg import EmulationConfig
from parallel import ParallelCore
from strategy.test_dev import TestFuture

# 默认配置文件目录
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
		#初始化并行执行控制接口
		self.paraCore = ParallelCore(config = self.emuCfg,
						dumpName = dumpName,
						debug = debug)

	# 启动合约执行线程
	def __setupContractProcess (self,
		contract,	#合约名称
		):
		strategy = TestFuture(contract = contract,
				      table = contract,
				      database = self.emuCfg.getDatabase(),
				      debug = True)

		strategy.setAttrs(maxPosAllowed = int(self.emuCfg.getContractAddMaxAllowed()),
				numPosToAdd = int(self.emuCfg.getContractVolumeAdd()),
				priceVariation = int(self.emuCfg.getContractTriggerLevel()),
				multiplier = int(self.emuCfg.getContractMultiplier()),
				dumpName = contract,
				paraCore = self.paraCore)

		thread.start_new_thread(threadContract, (strategy, ))

	# 开始
	def start (self):
		contracts = self.emuCfg.getContracts().split(',')

		# 确保所有合约被按序启动
		num = len(contracts)
		for idx in range(0, num):
			c = contracts[idx]
			if self.paraCore.allocManager(c):
				# 启动合约
				self.__setupContractProcess(c)
				# 确保线程按要求并行数量执行
				if self.paraCore.parallelStatus():
					continue

			self.paraCore.handleActions()

		# 所有合约都被执行或启动后，依然需要处理未结束合约的action
		while not self.paraCore.handleActions():
			continue
		# 确保合约先退出
		time.sleep(1)

# 合约线程启动入口
def threadContract(
	strategy,	#策略实例
	):
	#启动合约实例
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
