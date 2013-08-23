#! /usr/bin/python

'''
General Config Super Class.
	
	zhengwang.ruan@gmail.com
'''

import ConfigParser

class GenConfig:
	def __init__ (self, cfgFile):
		self.config = ConfigParser.ConfigParser()
		self.config.read(cfgFile)
		self.sectionList = self.config.sections()
		pass
	
	#def __exit__ (self):
		#pass
	
	#def validSection (self):
		#return True
	
	#def validOption (self):
		#return True
	
	def getSecOption (self, section, option):
		try:
			optVal = self.config.get(section, option)
		except:
			print "Bad option!"
			return None
		
		return optVal

