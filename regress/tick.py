#! /usr/bin/python

'''
Tick simulates a ticks source to Trading system. When tick varies 
(typically increase), it means a new trade cycle comes, Trading 
system needs to make decision if need to do any operation.

Ruan Zhengwang (ruan.zhengwang@gmail.com)
'''

import time

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
		
	# Timetick format.	
	def tickString (self, year, month, day):
		return '%s-%s-%s' % (year, month, day)
	
	# Get the time clock value for @tick
	def tickTime (self, tick):
		return time.strptime('%s' % tick, '%Y-%m-%d')
	
	# Get the year value in @tick
	def tickYear (self, tick):
		sep = tick.split('-')
		return int('%s' % sep[0])
		
	# Get the month value in @tick
	def tickMonth (self, tick):
		sep = tick.split('-')
		return int('%s' % sep[1])
	
	# Get the day value in @tick
	def tickDay (self, tick):
		sep = tick.split('-')
		return int('%s' % sep[2])
	
	# Get current tick.
	def curTick (self):
		return self.tickString(self.year, self.month, self.day)
	
	# Set current tick with @tick.
	def setCurTick (self, tick):
		self.year = self.tickYear(tick)
		self.month = self.tickMonth(tick)
		self.day = self.tickDay(tick)
		
	# Set and get next tick.
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
		#print 'Tick Src: New tick %s' % newTick
		return newTick
		
	# Judge if self.tick is leg behind a time tick.
	def curTickBehind (self, tick):
		t1 = time.strptime(self.curTick(), '%Y-%m-%d')
		t2 = time.strptime(tick, '%Y-%m-%d')
		
		#print self.curTick(), tick, t1 < t2
		
		return t1 < t2
		
#if __name__ == '__main__':
	#tick = Tick(2013, 1, 1)
	#while tick.curTick() < '2014-1-1':
		#print tick.tickNext()
	