# -*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2017年 07月 13日 星期四 23:33:02 CST

离散数据模块
"""

import os
import sys
sys.path.append("..")
import pandas as pd

from misc.debug import Debug


class Discrete:
	def __init__(self, xls, index_col = 0, quantiles = None, debug = False):
		"""
		将数据表离散化处理
		:param xls: 数据表
		:param index_col: 指定index列
		:param debug: 是否调试
		"""
		self.debug = Debug("Discrete", debug)
		self.xls = xls
		self.data = pd.read_excel(xls, index_col = index_col)
		# 默认分位点
		self.quantiles = pd.Series([0.1, 0.20, 0.35, 0.5, 0.65, 0.80, 0.9])
		if quantiles:
			self.quantiles = pd.Series(quantiles)
		# 数据转化时的临时存储区域
		self._desc = list()
		self._alias = None

	def __convert(self, value):
		"""
		将数据离散至各数据区间
		:param value: 需转化的数据列
		:return: 转化后数据
		"""
		ret = list()
		# 计算落在哪个区间
		i = 0
		for val in value:
			_type, _sect = self._desc[i]
			if _type == "p":
				_idx = _sect[val >= _sect].index[-1]
			else:
				# _type == "c"
				try:
					_idx = _sect[val >= _sect].index[-1]
					_idx += 1
				except IndexError:
					_idx = 0

			ret.append("%s_%s" % (self._alias[i], _idx))
			i += 1

		return ret

	def export(self, job, csvfile = None):
		"""
		导出数据
		:param job: 导出详细描述。如"((列名, ('c|p', [分位点, ...]), [别名]), [(....)])"
		:param csvfile: 导出文件名
		:return: None
		"""
		cols = map(lambda x: x[0], job)
		_data = self.data[cols].dropna()
		# 初始化导出的别名，没指定则用数据列名
		self._alias = map(lambda x: x[0] if len(x) < 3 else x[2], job)

		# 确定__convert所需的各列的分位信息：
		# 1.如果sections参数中有指定该列则用指定划分方式；
		# 2.否则默认启用分位点（self.quantiles）划分方式
		self._desc = list()
		for j in job:
			c = j[0]
			attr = j[1]
			jtype = attr[0]
			try:
				jbound = sorted(attr[1:])
			except IndexError, e:
				jbound = None

			if jtype == 'p':
				# 分位点划分。参数指定则使用指定值，否则使用默认分位点
				quantiles = self.quantiles
				if jbound:
					quantiles = jbound

				_sect = _data[c].astype("float").describe(quantiles).iloc[3:]
				self._desc.append(("p", _sect))

			elif jtype == 'c':
				# 区间划分。将数据划分为'len(jbound)+1'个区间，并由0开始记各区间
				_sect = pd.Series(jbound)
				self._desc.append(("c", _sect))
			else:
				self.debug.error("export: found unkown type '%s'" % jtype)
				return None

		output = map(self.__convert, _data.as_matrix().tolist())

		# 默认导出数据到和源文件同一目录
		if not csvfile:
			csvfile = "%s_DIS.csv" % self.xls.rstrip(".xls")
		else:
			csvfile = os.path.join(os.path.dirname(self.xls), csvfile)

		# pd.DataFrame(output).to_excel("%s_DIS.xlsx" % self.xls.rstrip(".xlsx"))
		pd.DataFrame(output).to_csv(csvfile, header = None, index = None)


def doTest():
	dis = Discrete("TESTDATA/discover/p15~11_mink_o15_3/TRANSACTIONS.xlsx", debug = True,
			quantiles = [0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9, 0.95])

	job = (("Float_Min", ['p'], "FLMin"),
		("Float_Max", ['p'], "FLMax"),
		("Profit", ['p'], "PR"),
		("FR_Min", ['p'], "FRMin"),
		("FR_Max", ['p'], "FRMax"))
	dis.export(job, csvfile = "test_1.csv")

	job = (("Profit", ['c', 0], "PR"),
		("FR_Max", ['c', 0.03, 0.06, 0.09], "FRMax"),
		("FR_Min", ['p'], "FRMin"))
	dis.export(job, csvfile = "test_2.csv")

	job = (("Profit", ['c', 0], "PR"),
		("FR_Max", ['c', 0.025, 0.03, 0.035, 0.04, 0.06, 0.09], "FRMax"))
	dis.export(job, csvfile = "test_3.csv")

	job = (("Profit", ['c', 0], "PR"),
		("FR_Max", ['c', 0.03], "FRMax"))
	dis.export(job, csvfile = "test_4.csv")

	job = (("FR_Min", ['c', -0.02, -0.01], "FRMin"),
		("PFR", ['c', -0.03, -0.02, -0.01, 0]))
	dis.export(job, csvfile = "test_5.csv")

	job = (("FR_Min", ['c', -0.016], "FRMin"),
		("PFR", ['c', 0]))
	dis.export(job, csvfile = "test_6.csv")

	job = (('FR_Max', ['c', 0.018], "FRMax0.018"),
		('FR_Max', ['c', 0.026], "FRMax0.026"),
		('FR_Max', ['c', 0.036], "FRMax0.036"),
		('FR_Max', ['c', 0.045], "FRMax0.045"),
		# ('FR_Max', ['c', 0.045]),
		('FR_Max', ['c', 0.050], "FRMax0.050"),
		('FR_Max', ['c', 0.088], "FRMax0.088"),
		('FR_Max', ['c', 0.125], "FRMax0.125"))
	dis.export(job, "test_7.csv")

if __name__ == "__main__":
	doTest()
