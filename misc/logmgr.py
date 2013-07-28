#! /usr/bin/python

'''
Log management.

Ruan Zhengwang (ruan.zhengwang@gmail.com)
'''

# Log management.
class Log:
	def __init__ (self, logName):
		self.logName = logName
		try:
			self.logObj = open(logName, 'w')
		except:
			print "Open log file '%s' failed!" % logName
			return
		return
	
	def __exit__ (self):
		self.logObj.close()
		return
	
	# Append a log at the end of log file.
	def append (self, logs):
		try:
			self.logObj.write('%s\n' % logs)
		except:
			print "Writing log to '%s' failed!" % self.logName
			return
		
	# Close the log file.
	def close (self):
		self.logObj.close()
