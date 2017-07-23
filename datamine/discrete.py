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

	def export(self, cols, sections = "{}", alias = None, csvfile = None):
		"""
		导出数据
		:param cols: 需转化的数据列
		:param sections: 指定数据列划分方式，如"{'c1': ['p', 0.4, 0.5, 0.8], 'c2': ['c', 0.03, 0.06]}"
		:param alias: 统计列使用别名
		:param csvfile: 导出文件名
		:return: None
		"""
		_data = self.data[cols]
		self._alias = alias if alias else cols
		sections = eval(sections)

		# 确定__convert所需的各列的分位信息：
		# 1.如果sections参数中有指定该列则用指定划分方式；
		# 2.否则默认启用分位点（self.quantiles）划分方式
		self._desc = list()
		for c in cols:
			if c not in sections.keys():
				# 参数中无指定，默认启用分位点方式
				_sect = _data[c].astype("float").describe(self.quantiles).iloc[3:]
				self._desc.append(("p", _sect))
			else:
				# 参数中有指定，且指定值中第一个值"c"表示区间划分，"p"表示分位点划分
				v = sections[c]
				if v[0] == "c":
					# 区间划分。将数据划分为 len(分位点)+1 个区间，区间由0开始记
					_sect = pd.Series(sorted(v[1:]))
					self._desc.append(("c", _sect))
				else:
					# 分位点划分
					_perc = v[1:] if v[0] == "p" else v
					_sect = _data[c].astype("float").describe(_perc).iloc[3:]
					self._desc.append(("p", _sect))

		output = map(self.__convert, _data.as_matrix().tolist())

		# 默认导出数据到和源文件同一目录
		if not csvfile:
			csvfile = "%s_DIS.csv" % self.xls.rstrip(".xls")
		else:
			csvfile = os.path.join(os.path.dirname(self.xls), csvfile)

		# pd.DataFrame(output).to_excel("%s_DIS.xlsx" % self.xls.rstrip(".xlsx"))
		pd.DataFrame(output).to_csv(csvfile, header = None, index = None)


def doTest():
	dis = Discrete("TESTDATA/discover/p15~11_mink_o15/TRANSACTIONS.xlsx", debug = True,
			quantiles = [0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9, 0.95])

	# dis.export(["Float_Min", "Float_Max", "Profit", "FR_Min", "FR_Max"],
	# 	alias = ["FLMin", "FLMax", "PR", "FRMin", "FRMax"], csvfile = "test.csv")

	dis.export(["Profit", "FR_Max", "FR_Min"], "{'Profit': ['c', 0], 'FR_Max': ['c', 0.03, 0.06, 0.09]}",
		["PR", "FRMax", "FRMin"], "test.csv_2")

if __name__ == "__main__":
	doTest()
