#! /usr/bin/python
#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2016年 03月 30日 星期三 22:47:59 CST

回归测试命令解析
"""

import sys
sys.path.append(".")

from misc.debug import Debug
from misc.execcmd import ExecCommand
from core.emulation import Emulation, ExceptionEmulUnknown, DEF_EMUL_CONFIG_DIR

# 默认关闭debug信息
debug = Debug('Regression', False)
# shell命令执行接口
shell = ExecCommand()

# 列出所有可选的测试配置文件
def listTestConfigs ():
	strCmd = "ls -l %s | sed \"1d\" | awk '{print $9}'" % DEF_EMUL_CONFIG_DIR
	shell.execCmd(strCmd)
	output = shell.getOutput()
	# debug.dbg("output: %s" % output)
	print output

# 回归测试入口
def startRegression (
	strategy,	#策略名
	test,		#测试配置名
	dump,		#dump数据表名
	dbgMode,	#调试开关
	):
	try:
		emulate = Emulation(cfg = test,
				dumpName = dump,
				strategy = strategy,
				debug = dbgMode)
		emulate.start()
	except ExceptionEmulUnknown, e:
		debug.error("startRegression: error: %s!" % e)
		return False

# 回归测试命令解析函数
def regressionOptionsHandler (
	options,	#选项集
	args,		#
	):
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

	if not options.dump:
		debug.error("Please specify a dump name.")
		return False

	return startRegression(options.strategy, options.test,
				options.dump, options.debug)

# 回归测试命令解析入口
def regressionOptionsParser (
	parser,	#
	):
	parser.add_option('-l', '--list', action="store_true", dest='list',
			help='List all test configurations.')
	parser.add_option('-s', '--strategy', dest='strategy',
			help='Select the test strategy.')
	parser.add_option('-t', '--test', dest='test',
			help='Select a test configuration.')
	parser.add_option('-d', '--dump', dest='dump',
			help='The name of dump table.')
	parser.add_option('-D', '--debug', action="store_true", dest='debug',
			help='Enable debug mode.')

	(options, args) = parser.parse_args()

	regressionOptionsHandler(options, args)
