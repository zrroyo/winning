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
	def __init__(self, xls, index_col = 0, debug = False):
		"""
		将数据表离散化处理
		:param xls: 数据表
		:param index_col: 指定index列
		:param debug: 是否调试
		"""
		self.debug = Debug("Discrete", debug)
		self.xls = xls
		self.data = pd.read_excel(xls, index_col = index_col)
		# 数据转化时的临时存储区域
		self._desc = None
		self._alias = None

	def __convert(self, value):
		"""
		将数据离散至各数据区间
		:param value: 需转化的数据列
		:return: 转化后数据
		"""
		_vc = zip(value, self._desc.columns)
		i = 0
		ret = list()
		for val, col in _vc:
			# 计算落在哪个区间
			_idx = self._desc[self._desc[col] <= val].index[-1]
			_col = self._alias[i] if self._alias else col
			ret.append("%s_%s" % (_col, _idx))
			i += 1

		return ret

	def export(self, cols, percentiles, alias = None, csvfile = None):
		"""
		导出数据
		:param cols: 需转化的数据列
		:param percentiles: 需统计的区间（列表）
		:param alias: 统计列使用别名
		:param csvfile: 导出文件名
		:return: None
		"""
		_data = self.data[cols]
		# 准备__convert需用到的数据
		self._desc = _data[cols].astype("float").describe(percentiles).iloc[3:]
		self._alias = alias

		output = map(self.__convert, _data.as_matrix().tolist())

		# 默认导出数据到和源文件同一目录
		if not csvfile:
			csvfile = "%s_DIS.csv" % self.xls.rstrip(".xls")
		else:
			csvfile = os.path.join(os.path.dirname(self.xls), csvfile)

		# pd.DataFrame(output).to_excel("%s_DIS.xlsx" % self.xls.rstrip(".xlsx"))
		pd.DataFrame(output).to_csv(csvfile, header = None, index = None)


def doTest():
	dis = Discrete("TESTDATA/discover/p15~11_mink_o15/TRANSACTIONS.xlsx", debug = True)

	dis.export(["Float_Min", "Float_Max", "Profit", "FR_Min", "FR_Max"],
		[0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9, 0.95],
		["FLMin", "FLMax", "PR", "FRMin", "FRMax"], "test.csv")

if __name__ == "__main__":
	doTest()
