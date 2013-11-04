#! /usr/bin/python

#from ctpapi import MdSpiDelegate, TraderSpiDelegate
from ctpapi import CtpMdApi, CtpTraderApi
#from mdmap import MarketDataMap
#from ctpagent import MarketDataAgent
from ctpagent import MarketDataAgent, TraderAgent
import time

class TestVar:
	happy = 1
	def __init__ (self):
		pass
	

def testMdApi():
	''' Test CtpMdApi '''
	
	#inst=[u'm1401', u'p1401']
	inst=[u'rb1401', u'm1401']
	#inst=[u'm1401']
	#mdSpi = CtpMdApi(inst, '1024', '00092', '888888', None)
	
	agent = ctpagent.MarketDataAgent()
	mdSpi = CtpMdApi(inst, '1024', '00000038', '123456', agent)
	mdSpi.Create("Md")
	mdSpi.RegisterFront('tcp://180.166.30.117:41213')
	mdSpi.Init()

	while 1:
		time.sleep(1)

def testTraderApi():
	''' Test TraderApi '''
	''' Test CtpMdApi '''
	
	#inst=[u'm1401', u'p1401']
	#inst=[u'rb1401', u'm1401']
	inst=[u'm1401']
	
	# v1
	#agent = TraderAgent(inst)
	#traderSpi = CtpTraderApi(inst, broker_id="1024",investor_id="00000038",passwd="123456", agent=agent)
	#traderSpi.Create("trader")
	#traderSpi.RegisterFront('tcp://180.166.30.117:41205')
	#traderSpi.Init()
	
	#v2
	agent = TraderAgent(inst, "1024", "00000038", "123456", 'tcp://180.166.30.117:41205')
	agent.init_init()
	
	agent.open_position('0', '3588', '1')
	
	while 1:
		time.sleep(1)
	
if __name__ == '__main__':
	#testMdApi()
	testTraderApi()
	