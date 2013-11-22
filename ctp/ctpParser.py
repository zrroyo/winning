#! /usr/bin/python
#-*- coding:utf-8 -*-

import sys
sys.path.append('..')
import thread
import time
from strategy.turt1 import Turt1
from misc.logmgr import Log
from misc.runstat import RunStat
from misc.runctrl import RunControl, RunCtrlSet
from ctp.ctpagent import MarketDataAgent, TraderAgent
from regress.emulate import CommonAttrs, emulationThreadEnd, Emulate
from regress.tick import Tick

def ctpThreadStart (strategy, futCode, runCtrl, **extraArgs):
	strt1 = None
	runStat = RunStat(futCode)
	
	if strategy == 'turt1':
		strt1 = Turt1 (futCode, '%s_dayk' % futCode, 'dummy', 'history', runStat)
		#strt1 = Turt1 (futCode, futCode, 'dummy', 'history', runStat)
	else:
		print "Bad strategy, only supports 'turt1' right now..."
		emulationThreadEnd(runCtrl)
		return
		
	# Enable storing logs.
	logTemp = 'logs/%s.log' % futCode	
	futLog = Log(logTemp)
	#runCtrl.enableStoreLogs(futLog)
	
	strt1.setAttrs(runCtrl.attrs.maxAddPos, runCtrl.attrs.minPos, 
			runCtrl.attrs.minPosIntv, runCtrl.attrs.priceUnit)
			
	curDay = time.strftime('%Y-%m-%d')
	
	mdAgent = extraArgs['md']
	tdAgent = extraArgs['td']
	# Enable emulation mode for strategy.	
	strt1.enableCTP(curDay, runCtrl, mdAgent, tdAgent)
	
	strt1.run()
	if strt1.runStat is not None:
		strt1.runStat.showStat()
		
	emulationThreadEnd(runCtrl)
		
#def startCtp(options, args):
def startCtp():
	#futList = ['m0401', 'm0501', 'm0601', 'm0701', 'm0801']
	#futList = ['m0401', 'm0409', 'm0501', 'm0509']
	#futList = ['m0401', 'm0409', 'm0501']
	futList = ['p1401', 'p1405']
	#futList.reverse()
	comAttr = CommonAttrs(4, 1, 40, 10)
	runCtrl1 = RunControl(False, thread.allocate_lock(), None, comAttr, False, '2013-4-30')
	runCtrl2 = RunControl(False, thread.allocate_lock(), None, comAttr, False, '2013-8-31')
	
	tickSrc = Tick(2013, 4, 15)
	
	runCtrlSet = RunCtrlSet(6, tickSrc)
	runCtrlSet.add(runCtrl1)
	runCtrlSet.add(runCtrl2)
	
	runCtrlSet.enableMarketRunStat()
	
	mdAgent = MarketDataAgent(futList, '1024', '00000038', '123456', 'tcp://180.166.30.117:41213')
	mdAgent.init_init()
		
	tdAgent = TraderAgent("1024", "00000038", "123456", 'tcp://180.166.30.117:41205')
	tdAgent.init_init()
	
	print 'Wait connecting...'
	time.sleep(2)
	
	emu = Emulate('turt1', runCtrlSet, futList, ctpThreadStart, md=mdAgent, td=tdAgent)
	emu.run()
		
def ctpOptionsHandler(options, args):
	pass
	
def ctpOptionsParser (parser):
	parser.add_option('-c', '--config', dest='config', 
			help='The detailed configuration file.')
	parser.add_option('-s', '--select', dest='select', 
			help='Select.')
	parser.add_option('-f', '--filter', dest='filter', 
			help='Filter.')
			
	(options, args) = parser.parse_args()

	ctpOptionsHandler(options, args)
	
if __name__ == '__main__':
	startCtp()
		