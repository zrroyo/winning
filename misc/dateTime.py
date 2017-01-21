#! /usr/bin/python
#-*- coding:utf-8 -*-

"""
时间处理模块
"""

import time
from datetime import datetime

def strToDatetime (timeStr, timeFormat = "%Y:%m:%d:%H:%M:%S"):
	"""
	把字符时间转换成指定的datetime格式
	:param timeStr: 时间字符串
	:param timeFormat: 时间格式,如 "%H:%M:%S"
	:return: datetime时间
	"""
	try:
		return datetime.strptime(timeStr, timeFormat)
	except ValueError, e:
		return None
		
def nowDatetime (timeFormat = None):
	"""
	返回当前时间。如指定timeFormat返回字符串，否则返回datetime时间。
	:param timeFormat: 时间格式,如 "%H:%M:%S"
	:return: 如指定timeFormat则返回字符串，否则返回datetime类型。
	"""
	now = datetime.now()
	if not timeFormat:
		return now

	return now.strftime(timeFormat)
	
def datetimeToStr (ptime, timeFormat = "%Y:%m:%d:%H:%M:%S"):
	"""
	把datetime时间转换成时间字符串
	:param ptime: datetime格式时间
	:param timeFormat: 时间格式,如 "%H:%M:%S"
	:return: 时间字符串
	"""
	return datetime.strftime(ptime, timeFormat)

def mkTimeInSeconds (timeStr, timeFormat = "%Y:%m:%d:%H:%M:%S"):
	"""
	将时间字符串转化为time.time（）时间
	:param timeStr: 时间字符串
	:param timeFormat: 时间格式,如 "%H:%M:%S"
	:return: 1979年以来秒数时间
	"""
	return time.mktime(strToDatetime(timeStr, timeFormat).timetuple())

#测试
if __name__ == '__main__':
	strTime = '2014:3:7:18:08:09'
	print strToDatetime(strTime, "%Y:%m:%d:%H:%M:%S")
	print strToDatetime(strTime, "%Y:%m:%d:%H:%M")
	print nowDatetime()
	print nowDatetime("%Y:%m:%d:%H:%M")
	print nowDatetime("%Y-%m-%d")
	print nowDatetime("%H:%M:%S")
	print strToDatetime("18:08:09", "%H:%M:%S")
	print datetimeToStr(nowDatetime(), "%d/%m/%Y")
	print mkTimeInSeconds(strTime, "%Y:%m:%d:%H:%M:%S")
