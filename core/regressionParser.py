#! /usr/bin/python
#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2016年 03月 30日 星期三 22:47:59 CST

回归测试命令解析
"""

import os
import sys
sys.path.append(".")
import time

from misc.debug import Debug
from misc.execcmd import ExecCommand
from core.tbase import DEF_EMUL_CONFIG_DIR
from core.emulation import Emulation
from core.execution import Execution

# 默认关闭debug信息
debug = Debug('Regression', False)
# shell命令执行接口
shell = ExecCommand()


def listTestConfigs():
	"""
	列出所有可选的测试配置文件
	:return: None
	"""
	configs = os.listdir(DEF_EMUL_CONFIG_DIR)
	# debug.dbg("output: %s" % configs)
	configs = '\n'.join(configs)
	print configs


def startRegression(options, strategy, test, argv, name, dbgMode, storeLog):
	"""
	启动测试
	:param options:
	:param strategy: 策略名
	:param test: 测试配置名
	:param argv: 命令参数列表
	:param name: 执行别名
	:param dbgMode: 调试开关
	:param storeLog: 保存日志
	:return: 成功返回True，否则返回False
	"""
	_start = time.time()

	if options.emulation:
		exc = Emulation(cfg = test,
				strategy = strategy,
				debug = dbgMode,
				storeLog = storeLog)
		exc.start(argv, name)
	else:
		exc = Execution(cfg = test,
				strategy = strategy,
				debug = dbgMode,
				storeLog = storeLog)

		if options.jobs:
			exc.start(argv, name, jobs = int(options.jobs))
		else:
			exc.start(argv, name)

	_end = time.time()
	debug.info("Time Execution: %ss" % (_end - _start))
	_start = _end
	exc.report(options.filter, options.rptname)
	_end = time.time()
	debug.info("Time Report: %ss" % (_end - _start))
	return True


def regressionOptionsHandler(options, argv):
	"""
	回归测试命令解析函数
	:param options: 选项集
	:param argv: 命令参数列表
	:return: 成功返回True，否则返回False
	"""
	if options.debug:
		global debug
		debug = Debug('Regression', True)

	if options.list:
		listTestConfigs()
		return True

	if not options.strategy:
		debug.error("Please select a strategy!")
		return False

	if not options.test:
		debug.error("Please select a test configuration!")
		return False

	return startRegression(options, options.strategy, options.test, argv,
			options.name, options.debug, options.storeLog)


def regressionOptionsParser(parser, argv):
	"""
	回归测试命令解析入口
	:param parser: OptionParser接口对象
	:param argv: 命令参数列表
	"""
	parser.add_option('-l', '--list', action="store_true", dest='list',
			help='List all test configurations.')
	parser.add_option('-s', '--strategy', dest='strategy',
			help='Select the test strategy.')
	parser.add_option('-t', '--test', dest='test',
			help='Select a test configuration.')
	parser.add_option('-n', '--name', dest='name',
			help='Name for a regress test.')
	parser.add_option('-e', '--emul', action="store_true", dest='emulation',
			help='Run tests in emulation mode.')
	parser.add_option('-j', '--jobs', dest='jobs',
			help='Maximum test jobs allowed.')
	parser.add_option('-S', '--storeLog', action="store_true", dest='storeLog',
			help='Store logs for each contract.')
	parser.add_option('-F', '--filter', dest='filter',
			help='Tag to filter reports.')
	parser.add_option('-R', '--rptname', dest='rptname',
			help='Report name for aggregate results.')
	parser.add_option('-D', '--debug', action="store_true", dest='debug',
			help='Enable debug mode.')

	(options, args) = parser.parse_args()

	regressionOptionsHandler(options, argv)
