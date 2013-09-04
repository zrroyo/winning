#-*- coding:utf-8 -*-

import logging

class c_instrument(object):
	@staticmethod
	def create_instruments(names,strategy,t2order=t2order_if):
		'''根据名称序列和策略序列创建instrument
		其中策略序列的结构为:
		[总最大持仓量,策略1,策略2...] 
		'''
		objs = dict([(name,c_instrument(name,t2order=t2order)) for name in names])
		for item in strategy.values():
			if item.name not in objs:
				logging.warning(u'策略针对合约%s不在盯盘列表中' % (item.name,))
				continue
			objs[item.name].max_volume = item.max_volume #
			objs[item.name].max_vtimes = item.max_vtimes #
			objs[item.name].max_lost = item.max_lost #            
			#objs[item.name].strategy = dict([(ss.get_name(),ss) for ss in item[1:]])
			objs[item.name].strategy = dict([(ss.name,ss) for ss in item.strategys])
			objs[item.name].initialize_positions()
		
		return objs

	def __init__(self,name,t2order = t2order_if):
		self.name = name
		#保证金率
		self.marginrate = (0,0) #(多,空)
		#合约乘数
		self.multiple = 0
		#最小跳动
		self.tick_base = 0  #单位为0.1
		#持仓量
		#BaseObject(hlong,hshort,clong,cshort) #历史多、历史空、今日多、今日空 #必须与实际数据一致, 实际上没用到
		self.position = BaseObject(hlong=0,hshort=0,clong=0,cshort=0)
		#持仓明细策略名==>Position #(合约、策略名、策略、基准价、基准时间、orderref、持仓方向、持仓量、当前止损价)
		self.position_detail = {}   #在Agent的ontrade中设定, 并需要在resume中恢复
		#设定的最大持仓手数
		self.max_volume = 1
		self.max_vtimes = 1  #最大的手次，如一次开2手，则为2手次
		self.max_lost = 0
		self.cur_vtimes = 0
		self.cur_profit = 0 #当前收益
	
		#应用策略 开仓函数名 ==> STRATEGY对象)
		self.strategy = {}
		
		#行情数据
		#其中tdata.m1/m3/m5/m15/m30/d1为不同周期的数据
		#   tdata.cur_min是当前分钟的行情，包括开盘,最高,最低,当前价格,持仓,累计成交量
		#   tdata.cur_day是当日的行情，包括开盘,最高,最低,当前价格,持仓,累计成交量, 其中最高/最低有两类，一者是tick的当前价集合得到的，一者是tick中的最高/最低价得到的
		self.t2order = t2order_if if hreader.is_if(self.name) else t2order_com
		#self.t2order = t2order
		##模拟的在外面解决
		#if int(time.strftime('%H%M%S')) > 170000:   #模拟
		#    self.t2order = t2order_mock
		#elif int(time.strftime('%H%M%S')) > 151500:   #模拟
		#    self.t2order = t2order_mock2
	
		self.data = BaseObject()
		self.begin_flag = False #save标志，默认第一个不保存, 因为第一次切换的上一个是历史数据
	
	def initialize_positions(self): #根据策略初始化头寸为0
		self.position_detail = dict([(ss.name,strategy.Position(self,ss)) for ss in self.strategy.values()])

	def calc_remained_volume(self):   #计算剩余的可开仓量
		if self.cur_vtimes >= self.max_vtimes:    #超过日开仓次数限制
			logging.info(u'超过日开仓手次限制:%s|%s' % (self.cur_vtimes,self.max_vtimes))
			return 0
		#if self.cur_profit <= -self.max_lost:   #超过日最大损失
		#    logging.info(u'超过日开损失限制:%s|%s' % (self.cur_profit,self.max_lost))
		#    return 0
		locked_volume = 0
		opened_volume = 0
		for position in self.position_detail.values():
			plocked,popened = position.get_locked_volume() 
			locked_volume += plocked
			opened_volume += popened
			logging.debug(u'计算策略锁定量: pos:%s,locked_volume=%s,opened_volume=%s' % (position,plocked,popened))
		
		remained_volume = self.max_volume - locked_volume if self.max_volume > locked_volume else 0
		logging.info(u'A_CRV2:%s合约总锁定数=%s,合约最大允许数=%s,剩余可开仓数=%s,已开仓数=%s' % (self.name,locked_volume,self.max_volume,remained_volume,opened_volume))
		
		return remained_volume

	def calc_margin_amount(self,price,direction):   
		'''
		计算保证金
		所有price以0.1为基准
		返回的保证金以1为单位
		'''
		#print self.name,self.marginrate[0],self.marginrate[1],self.multiple
		my_marginrate = self.marginrate[0] if direction == LONG else self.marginrate[1]
		print 'self.name=%s,price=%s,multiple=%s,my_marginrate=%s' % (self.name,price,self.multiple,my_marginrate)
		if self.name[:2].upper() == 'IF':
			#print 'price=%s,multiple=%s,my_marginrate=%s' % (price,self.multiple,my_marginrate)
			return price / 10.0 * self.multiple * my_marginrate * 1.05  #避免保证金问题
		else:
			return price * self.multiple * my_marginrate * 1.05

	def make_target_price(self,price,direction): 
		'''
		计算开平仓时的溢出价位
		传入的price以0.1为单位
		返回的目标价以1为单位
		'''
		return (price + SLIPPAGE_BASE * self.tick_base if direction == LONG else price-SLIPPAGE_BASE * self.tick_base)/10.0
	
	def get_order(self,vtime):
		#print self.t2order
		return self.t2order[vtime]
	
	def day_switch(self):
		self.cur_vtimes = 0
		self.cur_profit = 0
		for ss in self.strategy.values():   #重新初始化opener
			ss.opener = ss.opener_class()
		
	def add_vtimes(self,v):
		self.cur_vtimes += v
	
	def add_profit(self,profit):
		'''
		这个必须在平仓的时候计算，但是因为可能是一次指令多次回报(包括开仓和平仓)
		'''
		self.cur_profit += profit
		logging.info(u'当前利润:%s' % (self.cur_profit,))
