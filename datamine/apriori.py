#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
First Version Finished: 2016年 08月 27日 星期六 17:51:22 CST

This program is provided under the Gnu General Public License (GPL)
version 2 ONLY.
"""

import pandas as pd
import time
import itertools
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
		self.rules = []		#存储规则

	# 把矩阵元素组成unique序列
	def __unique (self,
		curKn,	#当前kn矩阵
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

	# 生成下一个kn矩阵
	def __getNextKn (self,
		curKn,	#当前kn矩阵
		unique,	#当前kn矩阵的unique序列
		):
		nextKn = pd.DataFrame()
		# unique中元素更少，代替curKn循环可提高效率
		for u in unique:
			tmp = pd.concat((curKn, pd.Series(u, index = curKn.index)), axis = 1)
			nextKn = pd.concat((nextKn, tmp), axis = 0)

		nColumns = len(nextKn.columns)
		nextKn.columns = xrange(nColumns)
		# self.debug.dbg("nextKn1: %s" % nextKn)
		nextKn = nextKn[ nextKn[nColumns - 2] < nextKn[nColumns - 1] ]
		nextKn.index = xrange(len(nextKn))
		return nextKn

	# 过滤kn中的有效组合
	def __knFilterValid (self,
		kn,	#kn矩阵
		):
		"""
		打印大型矩阵会导致性能严重下降，故关闭打印。
		"""
		_get_col = lambda x: self.data[x].as_matrix()
		# self.debug.dbg("__knFilterValid: kn: %s" % kn)
		_cols = map(_get_col, kn.T.as_matrix())
		# self.debug.dbg("__knFilterValid: _cols: %s" % _cols)
		_valid = reduce(lambda x, y: x * y, _cols)
		_valid = pd.DataFrame(_valid)
		# self.debug.dbg("__knFilterValid: _valid frame: %s" % _valid)
		supports = _valid.sum()/len(_valid)
		supports = supports[supports >= self.support]
		# self.debug.dbg("__knFilterValid: supports: %s" % supports)
		valid = kn.T[supports.index].T
		# self.debug.dbg("__knFilterValid: valid: %s" % valid)
		valid.index = xrange(len(valid))
		supports.index = valid.index
		return valid,supports

	# 计算Confidence（置信度）
	def __knConfidence (self,
		valid,		#kn的有效组合矩阵
		supports,	#支持度
		):
		"""
		将m x n矩阵转换成n个n-1阶子矩阵，再分别计算其每行的置信度。
		对于子矩阵C第m行的置信度为(support of valid[m]) / (support of C[m])
		"""
		# 得到所有子矩阵
		combs = list(itertools.combinations(valid.columns, len(valid.columns) - 1))
		# self.debug.error(combs)
		_get_sub_frame = lambda x: valid[list(x)]
		_sub_frames = map(_get_sub_frame, combs)

		# 求出子矩阵所有行的置信度
		_get_col = lambda x: self.data[x].as_matrix()
		for f in _sub_frames:
			# self.debug.error(f)
			_cols = map(_get_col, f.T.as_matrix())
			# self.debug.error(_cols)
			_valid = reduce(lambda x, y: x * y, _cols)
			_valid = pd.DataFrame(_valid)
			# self.debug.error(_valid)
			_support_counts = _valid.sum()/len(self.data)
			# self.debug.error(_support_counts)
			confidence = supports / _support_counts
			confidence = confidence[confidence > self.confidence]
			#存储rules
			self.__storeRules(valid, f, supports, confidence)

	# 存储rules
	def __storeRules (self,
		kn,		#kn矩阵
		comb,		#子矩阵
		supports,	#kn支持度
		confidence,	#置信度
		):
		_orderCol = list(comb.columns) + list(set(kn.columns) - set(comb.columns))
		_kn = kn[_orderCol]
		_rules = _kn.T[confidence.index].T
		supports = supports.T[confidence.index].T
		# self.debug.info(_rules)
		_func_rule = lambda x : " + ".join(x[0:len(x)-1]) + " --> " + x[len(x)-1]
		rules = map(_func_rule, _rules.as_matrix())
		self.rules += zip(rules, supports, confidence)

	# 列出所有rules
	def rules_ (self):
		print "{:<30}{:>10}{:>15} ".format('', 'Support', 'Confidence')
		for r in self.rules:
			print "{:<30}{:10.6f}{:15.6f} ".format(r[0], r[1], r[2])

	# 找出所有rules
	def __findRules (self,
		k0,	#初始k0矩阵
		):
		kn = k0
		unique = self.__unique(k0)
		# self.debug.dbg("__findRules: K0: %s" % k0)
		for i in xrange(1, len(k0)):
			print "正在进行第%s轮..." % i
			start = time.clock()

			nextKn = self.__getNextKn(kn, unique)
			# self.debug.dbg("__findRules: nextKn: %s" % nextKn)
			if len(nextKn) == 0:
				end = time.clock()
				self.debug.info("__findRules: time: %s" % (end - start))
				break

			kn, supports = self.__knFilterValid(nextKn)
			# self.debug.dbg("__findRules: Kn: %s" % kn)
			# unique = self.__unique(k0)
			unique = self.__unique(kn)
			# self.debug.dbg("__findRules: unique: len %s, values %s" % (len(unique), unique))
			# self.__storeRules(kn)
			self.__knConfidence(kn, supports)
			end = time.clock()
			self.debug.info("__findRules: time: %s" % (end - start))

	# 开始适配
	def fit (self,
		datafile,	#数据文件
		):
		data = pd.read_csv(datafile, header = None)
		ct = lambda x : pd.Series(1, index = x[pd.notnull(x)])
		data = map(ct, data.as_matrix())
		data = pd.DataFrame(data)
		data = data.fillna(0)
		self.data = data

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
