#! /usr/bin/python

import sys
sys.path.append("..")

import strategy as STRT
import regress.runstat as runstat
#
# Futures strategy super class which defines the most common methods 
# used to do futures business. Any futures strategy must inherit this 
# class so that the main framework could know how to interact with 
# a certain strategy.
#

class Futures(STRT.Strategy):
	def __init__ (self, futName, runStat=None):
		self.futName = futName		# The future name to test.
		self.maxAddPos = None		# The max actions allowd to add for a business.
		self.minPos = None		# The minimum unit to add positions.
		self.minPosIntv = None		# The minimum interval to add positions.
		self.priceUnit = None		# Price unit.
		self._pList = []		# The list to contain all positions.
		self.totalProfit = 0		# Total profit in one time of test.
		self.profit = 0			# The current profit for a time of business.
		self.runStat = runStat		# Count runtime statistics.
		
		return
	
	def __exit__ (self):
		return
	
	# The core method to run the whole test or business. Each strategy 
	# _MUST_ inherit this method and define your own one.
	def run (self):
		return
	
	# setAttrs() and checkAttrs() might be the key methods too, especially 
	# the tests which are sensitive to the values of maxAddPos, minPos, minPosIntv, 
	# etc. You need inherit and adjust these two method in your own occasions.
	def setAttrs (self, maxAddPos, minPos, minPosIntv, priceUnit):
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
		if self.curPostion() >= self.maxAddPos:
			return
		self._pList.append(price)
		print "		-->> Open: %s, poses %s <<--" % (price, self.curPostion())
		return self.curPostion()
		
	def openLongPostion (self, price):
		if self.curPostion() >= self.maxAddPos:
			return
		self._pList.append(price)
		print "		-->> Open: %s, poses %s <<--" % (price, self.curPostion())
		return self.curPostion()
		
	def closeShortPostion (self, price):
		if self.curPostion() == 0:
			return
		profit = self._pList.pop() - price
		profit *= self.minPos
		profit *= self.priceUnit
		self.profit += profit
		self.totalProfit += profit
		
		# If need do runtime statistics, update status.
		if self.runStat is not None:
			self.runStat.update(profit)
			
		print "		<<-- Close: profit %s, poses %s -->>" % (profit, self.curPostion())
		if self.curPostion() == 0:
			self.showProfit()
			# If need do runtime statistics, update status.
			if self.runStat is not None:
				self.runStat.updateBusinessProfit(self.profit)
			
		return self.curPostion()
	
	def closeLongPostion (self, price):
		if self.curPostion() == 0:
			return
		profit = price - self._pList.pop()
		profit *= self.minPos
		profit *= self.priceUnit
		self.profit += profit
		self.totalProfit += profit
		
		# If need do runtime statistics, update status.
		if self.runStat is not None:
			self.runStat.update(profit)
			
		print "		<<-- Close: profit %s, poses %s -->>" % (profit, self.curPostion())
		if self.curPostion() == 0:
			self.showProfit()
			# If need do runtime statistics, update status.
			if self.runStat is not None:
				self.runStat.updateBusinessProfit(self.profit)
			
		return self.curPostion()
		
	def closeAllPostion (self, price, short):
		while self.curPostion():
			if short is 'short':
				self.closeShortPostion(price)
			else:
				self.closeLongPostion(price)
					
		return self.curPostion()
			
	def closeMultPostion (self, poses, price, short):
		i = 0
		while self.curPostion() and i < poses:
			if short is 'short':
				self.closeShortPostion(price)
			else:
				self.closeLongPostion(price)
			i = i + 1
		
		return self.curPostion()
		
	# Export any assistant/helper information to users here.
	def assistant (self, extra):
		print '\nNo assistant found!\n'
		return
	