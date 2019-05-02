# -*- coding:utf-8 -*-

"""
CTP(返回的）错误解析模块
"""

import xml.dom.minidom as xdm


class CtpErrorParser(object):
	"""
	CTP错误解析类
	"""
	# 存储所有已定义的错误节点(minidom格式)
	errorNodes = None
	# 错误ID列表
	errorList = []

	def __init__(self, xmlFile):
		"""
		:param xmlFile: 定义错误ID的xml文件
		"""
		try:
			self.dom = xdm.parse(xmlFile)
			self.__initAllErrors()
		except:
			print(u'打开xml文件失败')
		
	def __initAllErrors(self):
		"""
		解析错误ID完成初始化
		"""
		# 得到所有已定义的错误节点
		self.errorNodes = self.dom.getElementsByTagName('error')
		
		# 生成错误ID列表，用于快速检查
		for node in self.errorNodes:
			self.errorList.append(node.getAttribute('value'))

	def getErrorMsgById(self, ErrorId):
		"""
		返回指定错误ID对应的错误提示
		:param ErrorId: 错误ID号
		"""
		# 检查是否是已知错误ID
		if str(ErrorId) not in self.errorList:
			return u'遇到未定义错误 ErrorId＝%d' % ErrorId
		
		# 检索错误ID对应的错误提示
		for node in self.errorNodes:
			if node.getAttribute('value') == str(ErrorId):
				return node.getAttribute('prompt')
			
	def errorMsgFactory(self, ErrorId):
		"""
		返回复合的错误提示
		:param ErrorId: 错误ID号
		"""
		errMsg = 'ErrID=%d,ErrMsg=%s' % (ErrorId, self.getErrorMsgById(ErrorId))
		return errMsg


# def doTest():
# 	parser = CtpErrorParser('futures/error.xml')
#
# 	print parser.getErrorMsgById(0)
# 	print parser.getErrorMsgById(2001)
# 	print parser.getErrorMsgById(333)
#
# 	print parser.errorMsgFactory(0)
# 	print parser.errorMsgFactory(2001)
# 	print parser.errorMsgFactory(333)
#
# if __name__ == '__main__':
# 	doTest()
#