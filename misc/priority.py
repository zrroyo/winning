#! /usr/bin/python

'''
Priority management.

Ruan Zhengwang (ruan.zhengwang@gmail.com)
'''

import time

class Priority:
	def __init__ (self):
		self.priorityDict = {}
		self.level = 0
		return
	
	def __exit__ (self):
		return
		
	# Relevel priority level.
	def _reLevel (self):
		self.level += 1
	
	# Add a new priority.
	def add (self, key):
		self._reLevel()
		self.priorityDict.setdefault(key, self.level)
		
	# Update priority for @key.
	def updatePriority (self, key):
		self._reLevel()
		#oldPri = self.priorityDict[key]
		self.priorityDict[key] = self.level
		return self.priorityDict[key]
		
	# List all priorities in reverse order.
	def listPriorities (self, reverse=False):
		return sorted(self.priorityDict.items(), key=lambda d:d[1], reverse=reverse)
	
	# Get the priority for @key.
	def getPriority (self, key):
		return self.priorityDict[key]
	
	# Do a micro HLT operation. This is intended for parallel run time situation in which 
	# multi threads are parallelly running, and the threads with lower priorities need halt
	# for somewhile to make sure those with higher priority be scheduled.
	def priorityHaltLoop (self):
		time.sleep(0.005)
		
