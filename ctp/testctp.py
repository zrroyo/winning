#! /usr/bin/python
#-*- coding:utf-8 -*-

import sys
import time
#from ctpapi import MdSpiDelegate, TraderSpiDelegate
from ctpapi import CtpMdApi, CtpTraderApi
from ctpagent import MarketDataAgent, TraderAgent
from futures import ApiStruct

class TestVar:
	happy = 1
	def __init__ (self):
		pass
	

def testMdApi():
	''' Test CtpMdApi '''
	
	#inst=[u'm1401', u'p1401']
	#inst=[u'rb1401', u'm1401']
	inst=[u'm1401']
	#mdSpi = CtpMdApi(inst, '1024', '00092', '888888', None)
	
	agent = MarketDataAgent()
	mdSpi = CtpMdApi(inst, '1024', '00000038', '123456', agent)
	mdSpi.Create("Md")
	mdSpi.RegisterFront('tcp://180.166.30.117:41213')
	mdSpi.Init()

	while 1:
		time.sleep(1)

def testTraderApi(price):
	''' Test TraderApi '''
	''' Test CtpMdApi '''
	
	#inst=[u'm1401', u'p1401']
	#inst=[u'rb1401', u'm1401']
	#inst=[u'm1401']
	inst=u'm1401'
	
	# v1
	#agent = TraderAgent(inst)
	#traderSpi = CtpTraderApi(inst, broker_id="1024",investor_id="00000038",passwd="123456", agent=agent)
	#traderSpi.Create("trader")
	#traderSpi.RegisterFront('tcp://180.166.30.117:41205')
	#traderSpi.Init()
	
	#v2
	agent = TraderAgent(inst, "1024", "00000038", "123456", 'tcp://180.166.30.117:41205')
	agent.init_init()
	
	price = int(price)
	agent.open_position(ApiStruct.D_Buy, price, 1)

	while 1:
		time.sleep(1)
	
if __name__ == '__main__':
	if len(sys.argv) < 2:
		print u'请指定测试功能：md／行情，td／交易'
		exit()
		
	if sys.argv[1] == 'md':
		testMdApi()
	elif sys.argv[1] == 'td':
		testTraderApi(sys.argv[2])
	