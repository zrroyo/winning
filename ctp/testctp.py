#! /usr/bin/python
#-*- coding:utf-8 -*-

import sys
sys.path.append('..')
import time
#from ctpapi import MdSpiDelegate, TraderSpiDelegate
from ctpapi import CtpMdApi, CtpTraderApi
from ctpagent import MarketDataAgent, TraderAgent
from futures import ApiStruct
from dataMgr.data import CtpData

class TestVar:
	happy = 1
	def __init__ (self):
		pass
	

def testMdApi():
	''' Test CtpMdApi '''
	
	#inst=[u'm1401', u'p1401']
	inst=['rb1401', 'm1401', 'p1401']
	#inst=[u'm1401']
	#mdSpi = CtpMdApi(inst, '1024', '00092', '888888', None)
	
	#v1
	#agent = MarketDataAgent()
	#mdSpi = CtpMdApi(inst, '1024', '00000038', '123456', agent)
	#mdSpi.Create("Md")
	#mdSpi.RegisterFront('tcp://180.166.30.117:41213')
	#mdSpi.Init()

	#v2
	agent = MarketDataAgent(inst, '1024', '00000038', '123456', 'tcp://180.166.30.117:41213')
	agent.init_init()
	#agent.start_monitor()
	
	#time.sleep(10)
	#print agent.dataMap.elemDict
	
	workDay = time.strftime('%Y-%m-%d')
	print workDay
	ctpData = CtpData('m1401', 'history', 'm1401_dayk', workDay, agent)
	while 1:
		time.sleep(1)
		#print agent.mdlocal.getClose(inst[0]), agent.mdlocal.getVolume(inst[0])
		#print agent.mdlocal.getClose(inst[1]), agent.mdlocal.getVolume(inst[1])
		#print agent.mdlocal.getClose(inst[2]), agent.mdlocal.getVolume(inst[2])
		print ctpData.getClose(workDay), ctpData.getOpen(workDay), ctpData.M10(workDay), ctpData.lowestBeforeDate(workDay, 5), ctpData.lowestUpToDate(workDay, 5), ctpData.highestBeforeDate(workDay, 5), ctpData.highestUpToDate(workDay, 5)
		

def testTraderApi(price):
	''' Test TraderApi '''
	''' Test CtpMdApi '''
	
	#inst=[u'm1401', u'p1401']
	#inst=[u'rb1401', u'm1401']
	#inst=[u'm1401']
	#inst=u'm1401'
	inst='m1401'
	
	# v1
	#agent = TraderAgent(inst)
	#traderSpi = CtpTraderApi(inst, broker_id="1024",investor_id="00000038",passwd="123456", agent=agent)
	#traderSpi.Create("trader")
	#traderSpi.RegisterFront('tcp://180.166.30.117:41205')
	#traderSpi.Init()
	
	#v2
	agent = TraderAgent(inst, "1024", "00000038", "123456", 'tcp://180.166.30.117:41205')
	agent.init_init()
	
	time.sleep(2)
	print 'Waiting.'

	price = int(price)
	#agent.open_position(ApiStruct.D_Buy, price, 1)
	#agent.open_position(ApiStruct.D_Buy, price, 1)
	agent.open_position(ApiStruct.D_Buy, price, 1)
	agent.open_position(ApiStruct.D_Buy, 3600, 1)
		
	##time.sleep(2)
	##print price
	##agent.close_position(ApiStruct.D_Sell, price, 1, ApiStruct.OF_CloseToday)
	#time.sleep(2)
	#print u'撤单:'
	#agent.cancel_command(inst, agent.order_ref)
	
	#time.sleep(2)
	#print u'查询: %s' % agent.order.OrderSysID
	#agent.querry_order(inst, agent.order.OrderSysID)
	
	print agent.orderMap.elemDict
	time.sleep(2)
	print u'撤单:'
	agent.cancel_command(inst, 2)
	time.sleep(1)
	print agent.orderMap.elemDict
	print agent.errOrderMap.elemDict
	
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
	