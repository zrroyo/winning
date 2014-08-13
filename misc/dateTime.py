#! /usr/bin/python
#-*- coding:utf-8 -*-

'''
时间处理模块
'''

from datetime import datetime

#把时间转换成指定的datetime格式
def strToDatetime (
	timeStr,				#时间字符串
	timeFormat = "%Y:%m:%d:%H:%M:%S",	#时间格式,如 "%H:%M:%S"
	):
	try:
		return datetime.strptime(timeStr, timeFormat)
	except:
		return None
		
#返回以指定datetime格式的当前时间
def nowDatetime (
	timeFormat = "%Y:%m:%d:%H:%M:%S", #时间格式,如 "%H:%M:%S"
	):
	strTimeNow = datetime.now().strftime(timeFormat)
	return datetime.strptime(strTimeNow, timeFormat)
	
#把datetime时间转换成字符串
def datetimeToStr (
	ptime,					#datetime格式时间
	timeFormat = "%Y:%m:%d:%H:%M:%S",	#时间格式,如 "%H:%M:%S"
	):
	return datetime.strftime(ptime, timeFormat)
	
#测试
if __name__ == '__main__':
	strTime = '2014:3:7:18:08:09'
	print strToDatetime(strTime, "%Y:%m:%d:%H:%M:%S")
	print strToDatetime(strTime, "%Y:%m:%d:%H:%M")
	print nowDatetime()
	print nowDatetime("%Y:%m:%d:%H:%M")
	print nowDatetime("%Y:%m:%M")
	print nowDatetime("%H:%M:%S")
	print strToDatetime("18:08:09", "%H:%M:%S")
	print datetimeToStr(nowDatetime(), "%d/%m/%Y")
	