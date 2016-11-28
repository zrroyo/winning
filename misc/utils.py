#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2016年 11月 28日 星期一 17:08:06 CST

公共工具模块
"""

def quickInsert (dest, val, start = 0, end = -1, descend = False,
		extract = lambda x: x):
	"""
	快速插入有序列表
	:param dest: 目标列表
	:param val: 待插入元素
	:param start: 开始索引
	:param end: 结束索引
	:param descend: 是否降序，默认为升序
	:param extract: 从复杂对象中提取比较元素接口
	:return: 无
	"""
	length = end - start
	if end < start:
		length = len(dest)
		end = length - 1

	mid = (start + end) / 2
	# print "DBG: start %s, mid %s, end %s;" % (start, mid, end)
	_vCmp = extract(val)
	if length == 0:
		dest.insert(0, val)
	elif (not descend and _vCmp < extract(dest[start])) or \
			(descend and _vCmp > extract(dest[start])):
		dest.insert(start, val)
	elif (not descend and _vCmp > extract(dest[end])) or \
			(descend and _vCmp < extract(dest[end])):
		dest.insert(end + 1, val)
	elif _vCmp == extract(dest[mid]):
		dest.insert(mid, val)
	elif mid == start:
		dest.insert(end, val)
	elif (not descend and _vCmp < extract(dest[mid])) or \
			(descend and _vCmp > extract(dest[mid])):
		quickInsert(dest, val, start, mid, descend, extract)
	else:
		quickInsert(dest, val, mid, end, descend, extract)

#
def doTest_quickInsert():
	# stack = []
	# values = [1, 9, 8, 10, 12, 4, 1, 4, 3, 7, 10, 7, 6, 15, 9, 3, 8]
	# print "values: %s" % values
	# for v in values:
	# 	# print "v: %s" % v
	# 	quickInsert(stack, v)
	# print stack

	stack = []
	values = [(6, 7), (9, 0), (8, 4), (1, 3), (9, 15), (7, 3), (1, 5), (14, 7)]
	print "values: %s" % values
	for v in values:
		quickInsert(stack, v, descend = True, extract = lambda x: x[1])
		# print "v: %s, stack: %s" % (v, stack)
	print stack

if __name__ == '__main__':
	doTest_quickInsert()
