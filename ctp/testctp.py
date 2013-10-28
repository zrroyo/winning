#! /usr/bin/python

#from ctpapi import MdSpiDelegate, TraderSpiDelegate
from ctpapi import CtpMdApi
#from mdmap import MarketDataMap
#from ctpagent import MarketDataAgent
import ctpagent
import time

class TestVar:
	happy = 1
	def __init__ (self):
		pass
	

def doTest():
	#inst=[u'm1401', u'p1401']
	inst=[u'rb1401', u'm1401']
	mdSpi = CtpMdApi(inst, '2030', '00092', '888888', None)
	
	#agent = ctpagent.MarketDataAgent()
	#mdSpi = CtpMdApi(inst, '2030', '00092', '888888', agent)
	mdSpi.Create("Md")
	mdSpi.RegisterFront('tcp://asp-sim2-md1.financial-trading-platform.com:26213')
	mdSpi.Init()

	while 1:
		time.sleep(1)

if __name__ == '__main__':
	doTest()