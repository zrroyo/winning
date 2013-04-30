#! /usr/bin/python

import traceback
import sys
import log

def excTraceBack ():
	try:
		return traceback.format_exc()
	except:
		return 'Exception in trace.'

def logExcSql ():
	log.log ('[SQL][Exc]: ', excTraceBack())
	return