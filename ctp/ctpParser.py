#! /usr/bin/python
#-*- coding:utf-8 -*-

'''
CTP子系统命令行选项解析、启动CTP服务
'''

import sys
sys.path.append('..')
import os
import thread
import time
from datetime import datetime
from strategy.turt1 import Turt1
from misc.logmgr import Log, LogPainter
from misc.runstat import RunStat
from misc.runctrl import RunControl, RunCtrlSet
from ctp.ctpagent import MarketDataAgent, TraderAgent
from ctp.autopos import CtpAutoPosition, OF_CloseToday
from regress.emulate import CommonAttrs, emulationThreadEnd, Emulate
from regress.tick import Tick
from futconfig import TradingConfig, CtpConfig
from misc.painter import Painter
from misc.futcom import tempNameSuffix

#CTP交易（模拟）执行线程入口
def ctpExecutionThreadStart (
	strategy,	#交易策略
	futCode,	#交易合约
	runCtrl,	#运行时控制单元
	**extraArgs	#其它参数
	):
	
	strt1 = None
	runStat = RunStat(futCode)
	
	database = extraArgs['database']

	if strategy == 'turt1':
		strt1 = Turt1 (futCode, '%s_dayk' % futCode, 'dummy', database, runStat)
	else:
		print "Bad strategy, only supports 'turt1' right now..."
		emulationThreadEnd(runCtrl)
		return
			
	#生成日志文件名后缀
	logNameSuffix = extraArgs['log']
	logDir = extraArgs['logDir']
	
	if logNameSuffix is not None:
		'''
		如果所传入的后缀名称不为空，则需要打开日志文件并记录。
		'''
		logTemp = '%s/%s-%s.log' % (logDir, futCode, logNameSuffix)
		futLog = Log(logTemp, True)
		strt1.enableStoreLogs(futLog)	#启动日志记录
	
	strt1.setAttrs(runCtrl.attrs.maxAddPos, runCtrl.attrs.minPos, 
			runCtrl.attrs.minPosIntv, runCtrl.attrs.priceUnit)
			
	curDay = time.strftime('%Y-%m-%d')
	
	mdAgent = extraArgs['md']
	tdAgent = extraArgs['td']
	logPainter = extraArgs['logPainter']
	startTime = extraArgs['startTime']
	
	#打开策略的CTP模式
	strt1.enableCTP(curDay, startTime, runCtrl, 
			mdAgent, tdAgent,
			logPainter, 
			logPainter.allocateLine()
			)
	
	strt1.run()
	#if strt1.runStat is not None:
		#strt1.runStat.showStat()
		
	emulationThreadEnd(runCtrl, strt1)
		
#行情显示线程入口
def marketDataThreadStart (
	painter,	#Painter描绘对象
	window,		#描绘(子)窗口
	mdAgent,	#行情数据代理接口
	):
	mdAgent.start_monitor(painter, window)
	
#检查是否是有效的交易策略
def isValidStrategy (strategy):
	return True
		
#CTP交易核心线程入口。从交易配置文件中读取参数并启动CTP交易。
def ctpTradeCoreThreadStart (
	trade,		#交易配置文件中的section名称
	tradeConfig,	#交易配置文件读取接口
	mdAgent,	#行情数据代理接口
	tdAgent,	#交易服务器端代理
	logPainter,	#CTP日志管理接口
	logDir		#存储log的指定目录
	):
	
	#得到所需交易合约列表，并倒序，因为Emulate会从最后一个合约开始倒序执行
	instruments = tradeConfig.getInstruments(trade).split(',')
	instruments.reverse()
	
	#填充通用交易属性
	comAttr = CommonAttrs(
		maxAddPos = int(tradeConfig.getMaxAddPos(trade)),
		minPos = int(tradeConfig.getMinPos(trade)),
		minPosIntv = int(tradeConfig.getMinPosIntv(trade)),
		priceUnit = int(tradeConfig.getPriceUnit(trade)),
		)
		
	#初始化运行控制单元
	startDate = tradeConfig.getStartDate(trade).split(',')
	
	runCtrl1 = RunControl(False, thread.allocate_lock(), 
			None, comAttr, False, 
			startDate[0]
			)
	runCtrl2 = RunControl(False, thread.allocate_lock(), 
			None, comAttr, False, 
			startDate[1]
			)
	
	#初始化Tick源
	tickSrc = Tick()
	tickSrc.reinit(startDate[0])
	
	#初始化运行控制单元集
	runCtrlSet = RunCtrlSet(
		maxAllowedPos = int(tradeConfig.getAllowedPos(trade)),
		tickSrc = tickSrc
		)
	runCtrlSet.add(runCtrl1)
	runCtrlSet.add(runCtrl2)
	
	#开启运行时统计信息
	#runCtrlSet.enableMarketRunStat()
	
	strategy = tradeConfig.getStrategy(trade)
	if isValidStrategy(strategy) == False:
		print u'检测到不合法的交易策略，不能启动执行，退出'
		return
		
	#生成日志文件名后缀
	logNameSuffix = tempNameSuffix()
		
	#得到交易启动时间
	startTime = tradeConfig.getTimeCtpOn(trade)
		
	#获取数据据表所在的数据库
	database = tradeConfig.getDatabase(trade)
		
	#启动CTP
	emu = Emulate(strategy, runCtrlSet, instruments, ctpExecutionThreadStart, 
			md=mdAgent, td=tdAgent, 
			log = logNameSuffix,	#log名称后缀
			logDir = logDir,	#存储log的指定目录
			logPainter = logPainter,#终端显示log的接口
			startTime = startTime,	#交易启动时间
			database = database	#数据表
			)
	emu.run()
		
#下单处理
def processOrder(
	details, 	#下单明细
	mdBrokerid, mdInvestor, mdPasswd, mdServer,
	tdBrokerid, tdInvestor, tdPasswd, tdServer
	):
		
	orderDetails = details.split(',')
	if len(orderDetails) != 4:
		print u'下单明细格式错误，正确格式例如：c,b,1,SR405'
		return
			
	orderType = orderDetails[0]
	direction = orderDetails[1]
	poses = int(orderDetails[2])
	instrument = orderDetails[3]
	
	print u'登录行情服务器...'
	
	#初始化并启动行情数据服务代理
	mdAgent = MarketDataAgent([instrument], mdBrokerid, mdInvestor, mdPasswd, mdServer)
	mdAgent.init_init()
	time.sleep(2)	#等待行情代理初始化完毕
		
	print u'登录交易服务器...'
	
	#初始化并启动交易服务器端代理
	tdAgent = TraderAgent(tdBrokerid, tdInvestor, tdPasswd, tdServer)
	tdAgent.init_init()
	time.sleep(1)	
		
	print u'开始下单...'
	
	autoPosMgr = CtpAutoPosition(mdAgent, tdAgent)
	
	#while 1:
		#print mdAgent.mdlocal.getClose(instrument)
		#time.sleep(0.5)

	try:
		
		if orderType == 'o' and direction == 'b':
			price = autoPosMgr.open_long_position(instrument, 
					mdAgent.mdlocal.getClose(instrument), poses)
			print u'开多成功，价格 %d' % price
		elif orderType == 'o' and direction == 's':
			price = autoPosMgr.open_short_position(instrument, 
					mdAgent.mdlocal.getClose(instrument), poses)
			print u'开空成功，价格 %d' % price
		elif orderType == 'c' and direction == 'b':
			price = autoPosMgr.close_long_position(instrument, 
					mdAgent.mdlocal.getClose(instrument), poses)
			print u'平多成功，价格 %d' % price
		elif orderType == 'c' and direction == 's':
			price = autoPosMgr.close_short_position(instrument, 
					mdAgent.mdlocal.getClose(instrument), poses)
			print u'平空成功，价格 %d' % price
	except:
		print "\n下单错误，退出"
		
#CTP子系统命令行选项解析主函数
def ctpOptionsHandler (options, args):
	if options.config is None:
		print "\n请用'-c'指定CTP全局配置文件.\n"
		return
		
	#检查CTP配置信息
	try:
		ctpConfig = CtpConfig(options.config)
		mdServer = ctpConfig.getServer('MarketData')
		mdPasswd = ctpConfig.getPasswd('MarketData')
		mdInvestor = ctpConfig.getInvestor('MarketData')
		mdBrokerid = ctpConfig.getBrokerid('MarketData')
		tdServer = ctpConfig.getServer('Trade')
		tdPasswd = ctpConfig.getPasswd('Trade')
		tdInvestor = ctpConfig.getInvestor('Trade')
		tdBrokerid = ctpConfig.getBrokerid('Trade')
	except:
		print u'获取CTP配置信息错误，退出'
		return
			
	#如要指定了下单模式则仅做下单操作
	if options.mode == 'order':
		if options.details is None:
			print u'order模式需要指定下单明细，退出'
			return
		
		processOrder(options.details,
			mdBrokerid, mdInvestor, mdPasswd, mdServer,
			tdBrokerid, tdInvestor, tdPasswd, tdServer
			)
		return
	
	if options.trading is None:
		print "\n请用'-t'指定交易配置文件.\n"
		return
	
	#如果指定了结束时间，则需要解析时间格式并设置
	if options.endTime is not None:
		etList = options.endTime.split(':')
		if len(etList) == 3:
			timeFormat = '%H:%M:%S'
		elif len(etList) == 6:
			timeFormat = '%Y:%m:%d:%H:%M:%S'
		else:
			print "\n指定的交易结束时间错误，退出.\n"
			return
		
		endTime = datetime.strptime(options.endTime, timeFormat)
			
	#确定可执行合约列表
	
	tradeConfig = TradingConfig(options.trading)

	#如果select选项生效，则只执行指定交易
	if options.select:
		sectionList = options.select.split(',')
	else:
		sectionList = tradeConfig.sectionList
		
	#如果reverse选项生效，则滤除指定交易
	if options.reverse:
		secList = []
		reverse = options.reverse.split(',')
		#print reverse
		for trade in sectionList:
			if not trade in reverse:
				secList.append(trade)
			
		sectionList = secList
		
	try:
		'''
		检查指定交易的执行标志是否打开，并生成合约列表
		'''
		tradings = []
		notAllowed = []
		for section in sectionList:
			if tradeConfig.getEnabled(section) == 'yes':
				tradings.append(section)
			else:
				notAllowed.append(section)
				
		if len(notAllowed) != 0:
			print u'未开启策略：%s' % notAllowed
		
		instruments = []
		for trade in tradings:
			instr = tradeConfig.getInstruments(trade).split(',')
			instruments += instr
			
		if len(instruments) != 0:
			print u'确定执行合约列表：%s' % instruments
		else:
			print u'没有可执行合约，退出'
			return
	except:
		print u'获取交易（策略）配置错误，退出'
		return
			
	#获取指定的终端窗口大小
	windowSize = options.window.split(',')
	if len(windowSize) < 3:
		print '所设窗口尺寸错误，退出'
		return
		
	height1 = int(windowSize[0])
	height2 = int(windowSize[1])
	width = int(windowSize[2])
	
	#初始化并启动行情数据服务代理
	mdAgent = MarketDataAgent(instruments, mdBrokerid, mdInvestor, mdPasswd, mdServer)
	mdAgent.init_init()
	time.sleep(2)	#等待行情代理初始化完毕
	
	#初始化终端描绘窗口
	painter = Painter()
	
	if options.mode == 'mar' or options.mode == 'com':
		'''
		如果在market或complex模式下运行，则打开行情显示。
		'''
		window1 = painter.newWindow('行情数据', height1, width, 0, 0)
		thread.start_new_thread(marketDataThreadStart, (painter, window1, mdAgent))
		
	if options.mode == 'mar':
		'''
		行情数据模式，并不提供交易服务
		'''
		try:
			while 1:
				time.sleep(1)
		except:
			painter.destroy()
			return
		
	#创建存储日志的目录
	cmdStr = 'mkdir -p %s' % options.logdir
	os.system(cmdStr)
	
	#启动交易部分
	try:
		#初始化并启动交易服务器端代理
		tdAgent = TraderAgent(tdBrokerid, tdInvestor, tdPasswd, tdServer)
		tdAgent.init_init()
		time.sleep(2)
	
		#print tradings
		
		window2 = painter.newWindow('交易跟踪', height2, width, height1+2, 0)
		logPainter = LogPainter(painter, window2, height2)
		
		#依次启动CTP交易
		for trade in tradings:
			thread.start_new_thread(ctpTradeCoreThreadStart, 
					(trade, tradeConfig, mdAgent, tdAgent, logPainter, options.logdir))
			time.sleep(0.1)
		
		#等待结束
		while 1:
			if options.endTime is not None:
				strTimeNow = datetime.now().strftime(timeFormat)
				timeNow = datetime.strptime(strTimeNow, timeFormat)
				if timeNow >= endTime:
					try:
						painter.destroy()
						print "\n交易时间到 '%s'，退出" % options.endTime
						exit()
					except:
						exit()
				else:
					time.sleep(60)
			else:
				time.sleep(60)
	except:
		painter.destroy()
		print u'\n执行被中断，退出'
		exit()
		
#CTP子系统命令行选项解析入口
def ctpOptionsParser (parser):
	parser.add_option('-c', '--config', dest='config', 
			help='The ctp global configuration file.')
	parser.add_option('-t', '--trading', dest='trading', 
			help='The trading configuration file.')
	parser.add_option('-s', '--select', dest='select', 
			help='Select a set of tradings to run.')
	parser.add_option('-r', '--reverse', dest='reverse', 
			help='Run the tradings which are reverse against this list.')
	parser.add_option('-m', '--mode', dest='mode', 
			help='Execution mode, such as, mar[ket](default), trade, com[plex], order.',
			default='mar')
	parser.add_option('-w', '--window', dest='window', 
			help="Window size, set using the format as h1,h2,width, the default is '14,14,123'",
			default='14,14,123')
	parser.add_option('-l', '--logdir', dest='logdir', 
			help="The directory to store logs, the default is 'logs'",
			default='logs')
	parser.add_option('-e', '--endTime', dest='endTime', 
			help="Time to end ctp trading and exit.")
	parser.add_option('-d', '--details', dest='details', 
			help="Details used according to each mode.")
			
	(options, args) = parser.parse_args()

	ctpOptionsHandler(options, args)
		