# -*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2017年 05月 29日 星期一 14:59:01 CST

合约执行模块，同时执行多个独立合约以提高效率。
"""

import os
import sys
sys.path.append("..")
import time
import re
import thread
import pandas as pd
import multiprocessing as mp

from misc.debug import Debug
from tbase import *
from corecfg import EmulationConfig, ContractDescConfig


class Execution(TBase):
	def __init__(self, cfg, strategy, debug = False, storeLog = False):
		"""
		合约执行
		:param cfg: 配置文件
		:param strategy: 策略名
		:param debug: 是否调试
		:param storeLog: 保存合约日志
		"""
		TBase.__init__(self, cfg, strategy, debug, storeLog)
		# 调试接口
		self.debug = Debug('Execution', debug)
		self.dbgMode = debug
		# 合约运行状态缓存数据结构，其中key为进程id
		self.procStates = {}
		#
		self.lock = thread.allocate_lock()

	def __setupContractProcess(self, contract, startTick, expireDates):
		"""
		启动合约执行
		:param contract: 合约名称
		:param startTick: 开始交易时间
		:param expireDates: 合约结束日期
		:return: None
		"""
		strategy = self.getInstance(contract)

		p = mp.Process(target = strategy.start, args = (startTick,
					self.estimateEndTick(contract, expireDates),
					None, None, None, self.storeLog, False))
		p.name = contract
		p.start()
		# 指定优先级
		self.procStates[p.pid] = [p, contract]
		self.debug.dbg("__setupContractProcess: new process %s, info %s" % (
							p.pid, self.procStates[p.pid]))
		# 启动线程等待合约结束，以使主线程启动其它合约
		thread.start_new_thread(threadWaitContract, (self, p))

	def start(self, argv, name, jobs = 4):
		"""
		测试入口
		:param argv: 命令参数列表
		:param name: 执行别名
		:param jobs: 并行任务数
		:return: 成功返回True，否则返回False
		"""
		# 初始化测试环境
		if not self.initTestEnv(argv, name):
			return False

		for c in self.contracts:
			# 支持从配置文件指定合约开始执行时间
			try:
				_startTick = self.startTicks.pop(0)
			except (IndexError, AttributeError):
				_startTick = None

			# 仅允许最多@jobs个任务同时进行
			while 1:
				self.lock.acquire()
				if len(self.procStates) < jobs:
					self.lock.release()
					break
				self.lock.release()
				time.sleep(0.1)

			# 启动合约进程
			self.__setupContractProcess(c, _startTick, self.expireDates)

		# 等待所有合约执行完毕
		while len(self.procStates):
			time.sleep(1)
			continue

	def report(self):
		"""
		生成全局统计报表
		:return: None
		"""
		files = os.listdir(self.logDir)
		ts = [f for f in files if re.search("TRADE_STAT[.]xlsx$", f)]
		ts = sorted(ts, reverse = True)
		total = pd.DataFrame()
		for t in ts:
			tmp = pd.read_excel(os.path.join(self.logDir, t), index_col = 0)
			if total.empty:
				total = tmp
			else:
				total = pd.concat((total, tmp), axis = 1)

		total = total.T
		total.index = range(1, len(total)+1)
		total.to_excel(os.path.join(self.logDir, "TRANSACTIONS.xlsx"))


def threadWaitContract(obj, proc):
	"""
	等待合约执行结束
	:param obj: Execution实例
	:param proc: Process实例
	"""
	proc.join()
	obj.lock.acquire()
	del obj.procStates[proc.pid]
	obj.lock.release()
	thread.exit_thread()
