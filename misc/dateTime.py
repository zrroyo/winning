#! /usr/bin/python
#-*- coding:utf-8 -*-

'''
时间处理模块
'''

from datetime import datetime

#把时间转换成指定的datetime格式，如果dataTime为None则用当前时间返回
def formatDatetime (
	timeFormat = "%Y:%m:%d:%H:%M:%S", #时间格式,如 "%H:%M:%S"
	dateTime = None,	#None则表示format当前时间
	):
		
	try:	
		if dateTime is None:
			strTimeNow = datetime.now().strftime(timeFormat)
			return datetime.strptime(strTimeNow, timeFormat)
		else:
			return datetime.strptime(dateTime, timeFormat)
	except:
			return None
		
#返回以指定datetime格式的当前时间
def nowDatetimeFormat (
	timeFormat = "%Y:%m:%d:%H:%M:%S", #时间格式,如 "%H:%M:%S"
	):
	timeNow = formatDatetime(timeFormat)
	return timeNow
	
#测试	
if __name__ == '__main__':
	strTime = '2014:3:7:18:08:09'
	print formatDatetime("%Y:%m:%d:%H:%M:%S", strTime)
	print formatDatetime("%Y:%m:%d:%H:%M", strTime)
	print formatDatetime("%Y:%m:%d:%H:%M")
	print nowDatetimeFormat()
	