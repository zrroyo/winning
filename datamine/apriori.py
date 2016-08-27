#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
First Version Finished: 2016年 08月 27日 星期六 17:51:22 CST

This program is provided under the Gnu General Public License (GPL)
version 2 ONLY.
"""

import pandas as pd
import time
from misc.debug import Debug

# 关联规则Apriori算法实现
class Apriori:

	def __init__(self,
		support,
		confidence,
		debug = False,
		):
		self.debug = Debug('Apriori', debug)
		self.support = support
		self.confidence = confidence
		self.data = None
		self.separator = '---'

	#
	def __unique (self,
		curKn,	#
		):
		if len(curKn.columns) <= 1:
			return list(curKn[0].unique())

		func_k_cols = lambda x : "curKn[%s]" % x
		columns = map(func_k_cols, curKn.columns)
		_strColumns = ",".join(columns)
		self.debug.dbg("_strColumns: %s" % _strColumns)
		unique = pd.concat((eval(_strColumns))).unique()
		unique.sort()

		# unique = pd.Series()
		# for col in curKn.columns:
		# 	unique = pd.concat((unique, curKn[col]), axis = 0)
		#
		# unique = unique.unique()
		# unique.sort()
		return list(unique)

	#
	def __getNextKn (self,
		curKn,	#
		unique,	#
		):
		nextKn = pd.DataFrame()
		#
		# lastCol = len(curKn.columns) - 1
		# for value in curKn.values:
		# 	valLastCol = value[lastCol]
		# 	uniIdx = unique.index(valLastCol)
		# 	remain = pd.Series(unique[uniIdx + 1:])
		# 	# remain = unique[uniIdx + 1:]
		# 	self.debug.dbg("__getNextKn: valLastCol %s, uniIdx %s, value %s" % (
		# 				valLastCol, uniIdx, value))
		# 	valMapIdx = pd.concat((pd.DataFrame([value], index = remain.index), remain), axis = 1)
		# 	nextKn = pd.concat((nextKn, valMapIdx), axis = 0)
		#
		# nextKn.index = xrange(len(nextKn))
		# nextKn.columns = xrange(len(nextKn.columns))
		# return nextKn

		# 减少循环次数可以提高效率
		for u in unique:
			tmp = pd.concat((curKn, pd.Series(u, index = curKn.index)), axis = 1)
			nextKn = pd.concat((nextKn, tmp), axis = 0)

		nColumns = len(nextKn.columns)
		nextKn.columns = xrange(nColumns)
		# self.debug.dbg("nextKn1: %s" % nextKn)
		nextKn = nextKn[ nextKn[nColumns - 2] < nextKn[nColumns - 1] ]
		nextKn.index = xrange(len(nextKn))
		return nextKn

	#
	def __knFilterValid (self,
		kn,
		):
		# import cProfile
		# cp = cProfile.Profile()
		# cp.clear()
		# cp.enable()

		_get_col = lambda x: self.data[x].as_matrix()
		# self.debug.dbg("__knFilterValid: kn: %s" % kn)
		_cols = map(_get_col, kn.T.as_matrix())
		self.debug.dbg("__knFilterValid: _cols: %s" % _cols)
		_valid = reduce(lambda x, y: x * y, _cols)
		_valid = pd.DataFrame(_valid)
		self.debug.dbg("__knFilterValid: _valid frame: %s" % _valid)
		supports = _valid.sum()/len(_valid)
		supports = supports[supports >= self.support]
		self.debug.dbg("__knFilterValid: supports: %s" % supports)
		valid = kn.T[supports.index].T
		self.debug.dbg("__knFilterValid: valid: %s" % valid)
		valid.index = xrange(len(valid))

		# cp.disable()
		# cp.print_stats(sort='cumtime')
		return valid

	#
	def registerRule (self,
		kn,
		):
		_rule = lambda x: self.separator.join(x)
		rules = map(_rule, kn.as_matrix())
		strRules = "\n".join(rules)
		print strRules

	#
	def __findRules (self,
		k0,
		):
		kn = k0
		unique = self.__unique(k0)
		self.debug.dbg("__findRules: K0: %s" % k0)
		for i in xrange(1, len(k0)):
			print "正在进行第%s轮..." % i
			start = time.clock()

			#
			nextKn = self.__getNextKn(kn, unique)
			self.debug.dbg("__findRules: nextKn: %s" % nextKn)
			if len(nextKn) == 0:
				end = time.clock()
				self.debug.info("__findRules: time: %s" % (end - start))
				break


			kn = self.__knFilterValid(nextKn)
			self.debug.dbg("__findRules: Kn: %s" % kn)
			unique = self.__unique(kn)
			self.debug.dbg("__findRules: unique: len %s, values %s" % (len(unique), unique))
			# self.registerRule(kn)
			end = time.clock()
			self.debug.info("__findRules: time: %s" % (end - start))

	#
	def fit (self,
		datafile,
		start = None,
		):
		data = pd.read_csv(datafile, header = None)
		# print "len(data) %s" % len(data)
		ct = lambda x : pd.Series(1, index = x[pd.notnull(x)])
		data = map(ct, data.as_matrix())
		data = pd.DataFrame(data)
		data = data.fillna(0)
		self.data = data
		# print self.data.head()

		#
		k0 = data.sum()/len(data)
		k0 = k0[k0 > self.support]
		k0 = pd.DataFrame(k0.index)
		# self.dbg("fit: k0: %s" % k0)
		start = time.clock()
		# import cProfile
		# cp = cProfile.Profile()
		# cp.clear()
		# cp.enable()
		self.__findRules(k0)
		# cp.disable()
		# cp.print_stats(sort='cumtime')
		end = time.clock()
		print (end - start)

