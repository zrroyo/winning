#! /usr/bin/python

'''
RunStat: runtime statistics.
'''

class RunStat:
	def __init__ (self, name):
		self.name = name	# The name for which do statistics.
		self.maxWin = 0		# The max profit won in a business.
		self.maxLoss = 0	# The max loss lost in a business.
		self.maxProfit = 0	# The max profit reached in a business.
		self.minProfit = 0	# The min profit reached in a business.
		self.maxBusProfit = 0	# The max profit made in a business.
		self.minBusProfit = 0	# The min profit made in a business.
		self.profit = 0		# The total profit made in a regression test.
		return
	
	def __exit__ (self):
		return
		
	# Update Max Win.
	def updateMaxWin (self, profit):
		if profit > self.maxWin:
			self.maxWin = profit
	
	# Update Max Loss.
	def updateMaxLoss (self, profit):
		if profit < self.maxLoss:
			self.maxLoss = profit
			
	## Update Max Profit.
	#def updateMaxProfit (self, profit):
		#if self.profit + profit > self.maxProfit:
			#self.maxProfit = self.profit + profit
		
	## Update Min Profit.
	#def updateMinProfit (self, profit):
		#if self.profit + profit < self.minProfit:
			#self.minProfit = self.profit + profit
	
	# Update business profit.
	def updateBusinessProfit (self, profit):
		# Update Max Profit.
		if profit > self.maxBusProfit:
			self.maxBusProfit = profit
			
		# Update Min Profit.
		if profit <  self.minBusProfit:
			self.minBusProfit = profit
			
	# Update Profit.
	def updateProfit (self, profit):
		# Update Max Profit.
		if self.profit + profit > self.maxProfit:
			self.maxProfit = self.profit + profit
			
		# Update Min Profit.
		if self.profit + profit < self.minProfit:
			self.minProfit = self.profit + profit
			
		self.profit += profit
	
	# Update all counted attributes.
	def update (self, profit):
		self.updateMaxWin(profit)
		self.updateMaxLoss(profit)
		self.updateProfit(profit)
		
	# Format the print.
	def _formatPrint (self, comment, value):
		print "		  %s:	%s" % (comment, value)
		
	# Show all counted attributes.
	def showStat (self):
		print "\n		* * * * * * * * * * * * * "
		print "		Show Run Time Statistics for [ %s ]:" % self.name
		self._formatPrint("      Max Order Win", self.maxWin)
		self._formatPrint("     Max Order Loss", self.maxLoss)
		self._formatPrint("Max Business Profit", self.maxBusProfit)
		self._formatPrint("Min Business Profit", self.minBusProfit)
		self._formatPrint("         Max Profit", self.maxProfit)
		self._formatPrint("         Min Profit", self.minProfit)
		self._formatPrint("       Total Profit", self.profit)
		print "		* * * * * * * * * * * * * \n"
	