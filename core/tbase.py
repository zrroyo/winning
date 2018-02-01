# -*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2017年 05月 22日 星期一 23:06:56 CST

模拟、回归测试基类
"""

import os
import sys
sys.path.append("..")
import importlib

from datetime import datetime
from misc.debug import Debug
from corecfg import EmulationConfig, ContractDescConfig

# 默认配置文件目录
DEF_EMUL_CONFIG_DIR = "tests"
# 默认合约描述文件
DEF_CONTRACT_DESC_CFG = "config/contracts_desc"
# 默认执行日志保存路径
DEF_TEST_OUT_DIR = "TESTDATA"


class TBase:
	def __init__(self, cfg, strategy, debug = False, storeLog = False):
		"""
		模拟、回归测试虚拟基类
		:param cfg: 配置文件
		:param strategy: 策略名
		:param debug: 是否调试
		:param storeLog: 保存合约日志
		"""
		# 调试接口
		self.debug = Debug('TBase', debug)
		self.dbgMode = debug
		self.storeLog = storeLog
		self.strategy = strategy
		#
		self.testCfg = os.path.join(DEF_EMUL_CONFIG_DIR, cfg)
		self.emuCfg = EmulationConfig(self.testCfg)
		self.contracts = self.emuCfg.getContracts().strip(',').split(',')
		self.expireDates = self.emuCfg.getExpireDates().strip(',')
		try:
			self.startTicks = self.emuCfg.getStartTime().split(',')
		except AttributeError:
			self.startTicks = None

		try:
			self.endTicks = self.emuCfg.getEndTime().split(',')
		except AttributeError:
			self.endTicks = None

		# 初始化合约描述接口
		self.descCfg = ContractDescConfig(DEF_CONTRACT_DESC_CFG)
		# 日志保存目录
		self.logDir = None

	def estimateEndTick(self, contract, expireDates):
		"""
		估计合约结束tick
		:param contract: 合约名称
		:param expireDates: 结束日期列表
		:return: 合约结束tick
		"""
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

		# self.debug.dbg("date_in_contract %s, expire map %s, year %s, month %s, ret %s" % (
		# 			date_in_contract, expireMap, year, month, ret))
		return ret

	def initTestEnv(self, argv, name):
		"""
		初始化测试前的执行环境
		:param argv: 命令参数列表
		:param name: 执行别名
		:return: 成功返回True，否则返回False
		"""
		# 创建测试目录名
		if not name:
			name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

		self.logDir = os.path.join(DEF_TEST_OUT_DIR, name)
		if os.path.exists(self.logDir):
			self.debug.error("'%s' already exists!" % self.logDir)
			return False

		self.debug.dbg("logDir: %s" % self.logDir)
		os.system("mkdir -p %s" % self.logDir)

		# 保存测试配置及命令，以免测试数据对不上
		os.system("cp -f %s %s/EMUL_CONFIG" % (self.testCfg, self.logDir))
		os.system("echo %s > %s/WIN_CMD" % (" ".join(argv), self.logDir))
		return True

	def getInstance(self, contract):
		"""
		:param contract: 合约名称
		:return: Future类执行实例
		"""
		try:
			mod = importlib.import_module("strategy.%s" % self.strategy)
			ret = mod.Main(contract = contract, config = self.descCfg,
					logDir = self.logDir, debug = self.dbgMode)

			ret.setAttrs(maxPosAllowed = int(self.emuCfg.getContractAddMaxAllowed()),
					numPosToAdd = int(self.emuCfg.getContractVolumeAdd()),
					priceVariation = int(self.emuCfg.getContractTriggerLevel()))
		except ImportError, e:
			self.debug.error("getInstance: %s" % e)
			ret = None

		return ret

	def start(self, argv, name):
		"""
		测试入口
		:param argv: 命令参数列表
		:param name: 执行别名
		:return: 成功返回True，否则返回False
		"""
		pass

	def report(self, filter, rptname):
		"""
		生成全局统计报表
		:param filter: 过滤器
		:param rptname: 导出报告名
		:return: None
		"""
		import re
		import pandas as pd
		files = os.listdir(self.logDir)
		ts = [f for f in files if re.search("%s[.]xlsx$" % filter, f)]
		ts = sorted(ts, reverse = True)
		total = pd.DataFrame()
		for t in ts:
			tmp = pd.read_excel(os.path.join(self.logDir, t), index_col = 0)
			total = pd.concat((total, tmp), axis = 0)

		total.index = range(1, len(total)+1)
		total.to_excel(os.path.join(self.logDir, "%s.xlsx" % rptname))
