#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2016年 05月 27日 星期五 13:50:54 CST

Confusion Matrix API
"""

# 生成混淆矩阵图
def cm_plot(
	y,	#
	yp,	#
	):
	from sklearn.metrics import confusion_matrix
	cm = confusion_matrix(y, yp)

	import matplotlib.pyplot as plt
	plt.matshow(cm, cmap=plt.cm.Greens)
	plt.colorbar()

	for x in range(len(cm)):
		for y in range(len(cm)):
			plt.annotate(cm[x,y], xy=(x, y),
				     horizontalalignment='center',
				     verticalalignment='center')

	plt.ylabel('True label')
	plt.xlabel('Predicted label')
	return plt
