# -*- coding:utf-8 -*-

"""
CTP(返回的）错误解析模块
"""

import os
import xml.dom.minidom as xdm


class CtpError(object):
	"""
	CTP错误解析类
	"""
	# CTP服务端出错代码表
	ERR_CODE_XML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "futures/error.xml")

	def __init__(self):
		# 存储所有已定义的错误节点(minidom格式)
		self.reasons = []
		# 得到所有已定义的错误节点
		self.dom = xdm.parse(CtpError.ERR_CODE_XML)
		self.reasons = self.dom.getElementsByTagName('error')

	def getErrReasonById(self, error_id):
		"""
		返回指定错误ID对应的错误提示
		:param error_id: 错误ID号
		"""
		ret = u'遇到未定义错误 ErrorId＝%d' % error_id
		for node in self.reasons:
			if node.getAttribute('value') == str(error_id):
				ret = node.getAttribute('prompt')
				break
		return ret

	def formatErrMsg(self, error_id):
		"""
		返回复合的错误提示
		:param error_id: 错误ID号
		"""
		errMsg = 'ErrID=%d,ErrMsg=%s' % (error_id, self.getErrReasonById(error_id))
		return errMsg


# def doTest():
# 	parser = CtpError()
#
# 	print parser.getErrReasonById(0)
# 	print parser.getErrReasonById(2001)
# 	print parser.getErrReasonById(333)
#
# 	print parser.formatErrMsg(0)
# 	print parser.formatErrMsg(2001)
# 	print parser.formatErrMsg(333)
#
# if __name__ == '__main__':
# 	doTest()
