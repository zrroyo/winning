#! /usr/bin/python

from ctpapi import MdSpiDelegate, TraderSpiDelegate

#THOST_TERT_RESTART  = 0
#THOST_TERT_RESUME   = 1
#THOST_TERT_QUICK    = 2

class TestVar:
	happy = 1
	def __init__ (self):
		pass
	

def doTest():
	mdSpi = MdSpiDelegate('m1401', '9000', '2600940', 'xxxx', None)
	mdSpi.Create("Md")
	mdSpi.RegisterFront('tcp://gfqh-md5.financial-trading-platform.com:41213')
	mdSpi.Init()
	#tSpi = TraderSpi()
	#tApi.RegisterSpi(tSpi)
	#tApi.SubscribePublicTopic(THOST_TERT_QUICK)
	#tApi.SubscribePrivateTopic(THOST_TERT_QUICK)
	#tApi.RegisterFront("tcp://172.16.0.31:26205")
	#tApi.Init()
	
	#var = TestVar()
	#print var.happy
	pass

if __name__ == '__main__':
	doTest()