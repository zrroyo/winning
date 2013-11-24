#-*- coding:utf-8 -*-

'''
轻量日志管理接口
	Ruan Zhengwang (ruan.zhengwang@gmail.com)
'''

#日志管理接口
class Log:
	def __init__ (self, 
		logName, 		#日志文件名
		quickFlush=False	#快速刷新模式
		):
		self.logName = logName
		self.quickFlush = quickFlush
		
		try:
			self.logObj = open(logName, 'w')
		except:
			print "Open log file '%s' failed!" % logName
			return
		return
	
	def __exit__ (self):
		self.logObj.close()
		return
	
	#追加日志
	def append (self, logs):
		try:
			self.logObj.write('%s\n' % logs)
			'''
			如果工作在快速刷新模式，则在每次写入后都应立即刷新到文件中。
			'''
			if self.quickFlush:
				self.logObj.flush()
		except:
			print "Writing log to '%s' failed!" % self.logName
			return
		
	#关闭日志文件
	def close (self):
		self.logObj.close()
