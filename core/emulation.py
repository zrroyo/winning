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

#模拟交易
class Emulation:
	def __init__ (self,
		cfg,		#配置文件
		dumpName,	#统计信息Dump名
		debug = False,	#是否调试
		):
		self.debug = Debug('Emulation', debug)	#调试接口
		self.emuCfg = EmulationConfig(cfg)	#模拟配置接口
		# 初始化并行执行控制接口
		self.paraCore = ParallelCore(config = self.emuCfg,
						dumpName = dumpName,
						debug = debug)

	# 计算符合配置的合约结束tick
	def __estimateEndTick (self,
		contract,
		expireDates,
		):
		date_in_contract = filter(str.isdigit, contract)
		year = int(date_in_contract[0:2])
		# 合约的实际结束日期应为交割月的上月
		month = int(date_in_contract[2:4])
		if month - 1 == 0:
			year -= 1

		# expireL = expireDates.split(',')
		# 将所有合约到期时间生成以月份为key的字典以加速查找
		# expireMap = dict([(int(ep.split('-')[0]), ep) for ep in expireL])
		expireL = [ep.split(':') for ep in expireDates.split(',')]
		expireMap = dict([(int(ep[0]), ep[1]) for ep in expireL])
		ep = expireMap[month]

		if year < 10:
			ret = "200%s-%s" % (year, ep)
		else:
			ret = "20%s-%s" % (year, ep)

		self.debug.dbg("date_in_contract %s, expire map %s, year %s, month %s, ret %s" % (
					date_in_contract, expireMap, year, month, ret))
		return ret

	# 启动合约执行线程
	def __setupContractProcess (self,
		contract,	#合约名称
		startTick,	#开始交易时间
		expireDates,	#合约结束日期
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

		thread.start_new_thread(threadContract, (strategy, startTick,
						self.__estimateEndTick(contract, expireDates)))

	# 开始
	def start (self):
		contracts = self.emuCfg.getContracts().strip(',').split(',')
		startTicks = self.emuCfg.getStartTime().strip(',').split(',')
		expireDates = self.emuCfg.getExpireDates().strip(',')

		# 需按序启动所有合约
		num = len(contracts)
		for idx in range(0, num):
			c = contracts[idx]
			if self.paraCore.allocManager(c):
				# 尽量按配置指定开始时间启动合约
				try:
					tick = startTicks[idx]
				except IndexError:
					tick = None

				self.__setupContractProcess(c, tick, expireDates)
				# 如并行数量不满则继续启动线程
				if self.paraCore.parallelStatus():
					continue

			self.paraCore.handleActions()

		# 所有合约都被启动后，依然需继续处理未结束合约的action
		while not self.paraCore.handleActions():
			continue
		# 所有合约执行完，确保合约先退出
		time.sleep(0.1)

# 合约线程启动入口
def threadContract(
	strategy,	#策略实例
	startTick,	#开始交易时间
	stopTick,	#停止交易时间
	):
	#启动合约实例
	strategy.start(startTick, stopTick)

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
