#! /usr/bin/python

#from ctpapi import MdSpiDelegate, TraderSpiDelegate
from ctpapi import CtpMdApi
import time

#THOST_TERT_RESTART  = 0
#THOST_TERT_RESUME   = 1
#THOST_TERT_QUICK    = 2

class TestVar:
	happy = 1
	def __init__ (self):
		pass
	

def doTest():
	inst=[u'm1401', u'p1401']
	mdSpi = CtpMdApi(inst, '2030', '00092', '888888', None)
	mdSpi.Create("Md")
	mdSpi.RegisterFront('tcp://asp-sim2-md1.financial-trading-platform.com:26213')
	mdSpi.Init()

	while 1:
		time.sleep(1)

if __name__ == '__main__':
	doTest()