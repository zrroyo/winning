#-*- coding:utf-8 -*-

'''
轻量日志管理接口
	Ruan Zhengwang (ruan.zhengwang@gmail.com)
'''

import thread
from painter import Painter

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
	
	def __del__ (self):
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
	
	
#窗口日志(Painter)管理接口
class LogPainter:
	def __init__ (self, 
		painter,	#Painter描绘对象
		window, 	#描绘窗口
		lines		#窗口总行数
		):
		self.painter = painter
		self.window = window
		self.lines = lines
		self.lock = thread.allocate_lock()
		self.__line = 0		#分配起始行
		
	#描绘一行
	def paintLine (self, lineNo, logMsg):
		self.painter.paintLine(self.window, lineNo, logMsg)
		
	#分配显示行
	def allocateLine (self):
		self.lock.acquire()
		if self.__line < self.lines:
			line = self.__line
			self.__line += 1
			#print u'已分配%d行' % line
			self.lock.release()
			return line
		else:	
			print u'LogPainter: 窗口没有显示行可用，已分配完'
			self.lock.release()
			return None
		