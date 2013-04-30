#! /usr/bin/python

import strategy as STRT

#
# Futures strategy super class which defines the most common methods 
# used to do futures business. Any futures strategy must inherit this 
# class so that the main framework could know how to interact with 
# a certain strategy.
#

class Futures(STRT.Strategy):
	def openShortPostion (self):
		return
		
	def openLongPostion (self):
		return
		
	def closeShortPostion (self):
		return
		
	def closeLongPostion (self):
		return
		
	def isBreakThrough (self):
		return
	
	def run (self):
		return
	