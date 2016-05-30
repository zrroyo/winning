#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2016年 05月 27日 星期五 13:50:54 CST

ROC (Receiver Operating Characteristic) Curve API
"""

# 生成ROC图
def roc_plot (
	x,	#x轴
	y,	#y轴
	label,	#标签
	):
	from sklearn.metrics import roc_curve
	import matplotlib.pyplot as plt

	fpr, tpr, threshold = roc_curve(x, y, pos_label = 1)
	fig = plt.figure()
	plt.plot(fpr, tpr, linewidth=2, label = label)
	plt.xlabel("False Positive Rate")
	plt.ylabel("True Positive Rate")
	plt.ylim(0,1.05) #边界范围
	plt.xlim(0,1.05) #边界范围
	plt.legend(loc=4) #图例
	plt.show()
	return fig
