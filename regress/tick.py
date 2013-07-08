#! /usr/bin/python

'''
Tick simulates a ticks source to Trading system. When tick varies 
(typically increase), it means a new trade cycle comes, Trading 
system needs to make decision if need to do any operation.

Ruan Zhengwang (ruan.zhengwang@gmail.com)
'''

#import time

class Tick:
	def __init__ (self, year=1990, month=1, day=1):
		self.year = year
		self.month = month
		self.day = day
		return
	
	def __exit__ (self):
		return
	
	# Return the max day in month.
	def _maxDayInMonth (self, month, Year):
		if month == 1:
			maxDay = 31
		elif month == 2:
			if Year % 4 == 0:
				maxDay = 29
			else:
				maxDay = 28
		elif month == 3:
			maxDay = 31
		elif month == 4:
			maxDay = 30
		elif month == 5:
			maxDay = 31
		elif month == 6:
			maxDay = 30
		elif month == 7:
			maxDay = 31
		elif month == 8:
			maxDay = 31
		elif month == 9:
			maxDay = 30
		elif month == 10:
			maxDay = 31
		elif month == 11:
			maxDay = 30
		elif month == 12:
			maxDay = 31
		else:
			return None
		
		return maxDay
		
	def tickString (self, year, month, day):
		return '%s-%s-%s' % (year, month, day)
	
	def tickTime (self, tick):
		return time.strptime('%s' % tick, '%Y-%m-%d')
	
	def curTick (self):
		return self.tickString(self.year, self.month, self.day)
	
	def tickYear (self, tick):
		sep = tick.split('-')
		return '%s' % sep[0]
		
	def tickMonth (self, tick):
		sep = tick.split('-')
		return '%s' % sep[1]
	
	def tickDay (self, tick):
		sep = tick.split('-')
		return '%s' % sep[2]
		
	def tickNext (self):
		year = self.year
		month = self.month
		day = self.day + 1
		
		if day > self._maxDayInMonth(month, year):
			day = 1 
			month += 1
			if month > 12:
				year += 1
				month = 1
		
		self.year = year
		self.month = month
		self.day = day
		newTick = self.tickString(year, month, day)
		return newTick
		
#if __name__ == '__main__':
	#tick = Tick(2013, 1, 1)
	#while tick.curTick() < '2014-1-1':
		#print tick.tickNext()
	