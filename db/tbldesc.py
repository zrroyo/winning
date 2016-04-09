#-*- coding:utf-8 -*-

'''
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2015年 05月 17日 星期日 17:23:49 CST

数据表描述
'''

#数据表字段(Field)
F_TIME		= 'Time'
F_OPEN		= 'Open'
F_HIGH		= 'High'
F_LOW		= 'Low'
F_CLOSE		= 'Close'
F_AVG		= 'Avg'
F_VOLUME	= 'Volume'
F_OPENINTEREST	= 'OpenInterest'
F_TR		= 'Tr'
F_ATR		= 'Atr'

#数据表查询完成后返回的列表中的索引号(Field Number)
FN_TIME		= 0
FN_OPEN		= 1
FN_HIGH		= 2
FN_LOW		= 3
FN_CLOSE	= 4
FN_AVG		= 5
FN_VOLUME	= 6
FN_OPENINTEREST	= 7
FN_TR		= 8
FN_ATR		= 9

# 字段名称到字段号映射表
DATA_TBL_F_FN_MAP = {
	F_TIME		: FN_TIME,
	F_OPEN		: FN_OPEN,
	F_HIGH		: FN_HIGH,
	F_LOW		: FN_LOW,
	F_CLOSE		: FN_CLOSE,
	F_AVG		: FN_AVG,
	F_VOLUME	: FN_VOLUME,
	F_OPENINTEREST	: FN_OPENINTEREST,
	F_TR		: FN_TR,
	F_ATR		: FN_ATR
}

#交易单统计（Order Stat Dump）表字段
OSD_F_ID		= 'DumpID'
OSD_F_CONTRACT		= 'Contract'
OSD_F_TICK_OPEN		= 'TickOpen'
OSD_F_OPEN		= 'OpenPrice'
OSD_F_TICK_CLOSE	= 'TickClose'
OSD_F_CLOSE		= 'ClosePrice'
OSD_F_DIRECTION		= 'Direction'
OSD_F_VOLUME		= 'Volume'
OSD_F_PROFIT		= 'Profit'

#利润统计（Profit Stat Dump）表字段
PSD_F_ID		= 'DumpID'
PSD_F_CONTRACT_START	= 'StartContract'
PSD_F_CONTRACT_END	= 'EndContract'
PSD_F_TICK_START	= 'StartTick'
PSD_F_TICK_END		= 'EndTick'
PSD_F_MAX_FLOAT		= 'MaxFloat'
PSD_F_MAX_TICK		= 'MaxFloatTick'
PSD_F_MIN_FLOAT		= 'MinFloat'
PSD_F_MIN_TICK		= 'MinFloatTick'
PSD_F_FINAL		= 'Final'
