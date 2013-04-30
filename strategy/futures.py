#! /usr/bin/python

import strategy as STRT

#
# Futures strategy super class which defines the most common methods 
# used to do futures business. Any futures strategy must inherit this 
# class so that the main framework could know how to interact with 
# a certain strategy.
#

class Futures(STRT.Strategy):
	def __init__ (self, futName):
		self.futName = futName		# The future name to test.
		self.maxPos = None		# The maximum positions a business allowes to add.
		self.minPos = None		# The minimum unit to add positions.
		self.minPosIntv = None		# The minimum interval to add positions.
		self._pList = []		# The list to contain all positions.
		self.totalProfit = 0		# Total profit in one time of test.
		self.profit = 0			# The current profit for a time of business.
		
		return
	
	def __exit__ (self):
		return
	
	# The core method to run the whole test or business. Each strategy 
	# _MUST_ inherit this method and define your own one.
	def run (self):
		return
	
	# setAttrs() and checkAttrs() might be the key methods too, especially 
	# the tests which are sensitive to the values of maxPos, minPos, minPosIntv, 
	# etc. You need inherit and adjust these two method in your own occasions.
	def setAttrs (self, maxPos, minPos, minPosIntv):
		return
		
	def checkAttrs (self):
		return False
			
	def showProfit (self):
		print "		++++++ Business profit %s ++++++" % (self.profit)
		print "		****** Total profit %s ******" % (self.totalProfit)
	
	# Position Management Methods.
	def curPostion (self):
		return len(self._pList)
	
	def emptyPostion (self):
		self._pList = []
		self.profit = 0
	
	def openShortPostion (self, price):
		if self.curPostion() >= self.maxPos:
			return
		self._pList.append(price)
		print "		-->> Open: %s, poses %s <<--" % (price, self.curPostion())
		return self.curPostion()
		
	def openLongPostion (self, price):
		if self.curPostion() >= self.maxPos:
			return
		self._pList.append(price)
		print "		-->> Open: %s, poses %s <<--" % (price, self.curPostion())
		return self.curPostion()
		
	def closeShortPostion (self, price):
		if self.curPostion() == 0:
			return
		profit = self._pList.pop() - price
		self.profit += profit
		self.totalProfit += profit
		print "		<<-- Close: profit %s, poses %s -->>" % (profit, self.curPostion())
		if self.curPostion() == 0:
			self.showProfit()
			
		return self.curPostion()
	
	def closeLongPostion (self, price):
		if self.curPostion() == 0:
			return
		profit = price - self._pList.pop()
		self.profit += profit
		self.totalProfit += profit
		print "		<<-- Close: profit %s, poses %s -->>" % (profit, self.curPostion())
		if self.curPostion() == 0:
			self.showProfit()
			
		return self.curPostion()
		
	def closeAllPostion (self, price, short):
		while self.curPostion():
			if short is 'short':
				poses = self.closeShortPostion(price)
			else:
				poses = self.closeLongPostion(price)
					
		return self.curPostion()
			
	def closeMultPostion (self, poses, price, short):
		i = 0
		while self.curPostion() and i < poses:
			if short is 'short':
				poses = self.closeShortPostion(price)
			else:
				poses = self.closeLongPostion(price)
			i = i + 1
		
		return self.curPostion()
		