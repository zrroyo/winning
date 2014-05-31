#-*- coding:utf-8 -*-

'''
配置文件(通用)读取接口
	zhengwang.ruan@gmail.com
'''

import ConfigParser

class GenConfig:
	def __init__ (self, cfgFile):
		self.config = ConfigParser.ConfigParser()
		self.config.read(cfgFile)
		self.sectionList = self.config.sections()
		pass
	
	#def validSection (self):
		#return True
	
	#def validOption (self):
		#return True
	
	def getSecOption (self, section, option):
		try:
			optVal = self.config.get(section, option)
			return optVal
		except:
			#print "Bad option!"
			return None
		