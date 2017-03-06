#! /usr/bin/python
#-*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2015年 11月 21日 星期六 17:36:12 CST

模拟交易、回归测试核心模块
"""

import os
import sys
sys.path.append("..")
import time
import ctypes
import Queue
import multiprocessing as mp
from datetime import datetime

from misc.debug import Debug
from misc.utils import quickInsert
from misc.dateTime import mkTimeInSeconds
from corecfg import EmulationConfig, ContractDescConfig

# 默认配置文件目录
DEF_EMUL_CONFIG_DIR = "tests"
# 默认合约描述文件
DEF_CONTRACT_DESC_CFG = "config/contracts_desc"
# 默认执行日志保存路径
DEF_TEST_OUT_DIR = "TESTDATA"

# 合约调度状态
EMUL_SCHED_MODE_NSP		= 1
EMUL_SCHED_MODE_OSP		= 2

# Sched请求类型
EMUL_REQ_ACK			= 0
EMUL_REQ_NSP_CLOSE		= 1
EMUL_REQ_OSP_CLOSE		= 2
EMUL_REQ_NSP_OPEN		= 4
EMUL_REQ_END			= 8
EMUL_REQ_INVALID		= -1

# NP请求（仅通知无需等待）列表
EMUL_REQ_NP_LIST = [EMUL_REQ_NSP_CLOSE]

# 合约操作描述
MEUL_FUT_ACT_SKIP	= 0
EMUL_FUT_ACT_OPEN	= 1
EMUL_FUT_ACT_CLOSE	= 2

class ReqMsg:
	def __init__ (self):
		"""
		Sched请求数据结构
		"""
		self.mode = EMUL_SCHED_MODE_NSP		#合约同步点（SP）状态
		self.type = EMUL_REQ_INVALID		#请求类型
		self.tick = None			#请求时tick时间，为秒数
		self.pid = -1				#合约进程id
		self.pos = 0				#申请仓位
		self.capital = 0.0			#申请资金
		self.wait = {}			#等待进程表

class ReqStack:
	def __init__ (self, debug = False):
		"""
		请求管理队列。
		:param debug: 打开调试模式
		"""
		self.debug = Debug('ReqStack', debug)	#调试接口
		self.stack = []	#按req.tick从大到小排列
		self.rare = {}	#特殊请求队列

	def insert (self, req, rare = False):
		"""
		在队列中插入请求。
		:param req: 请求
		:param rare: 特殊标记
		:return: None
		"""
		quickInsert(self.stack, req, descend = True, extract = lambda x: x.tick)
		# 对于特殊请求（比如current为0），需要标记以便快速查找
		if rare:
			self.rare[req.pid] = req
			self.debug.dbg("insert: rare %s" % self.rare)

	def len (self):
		"""
		返回队列长度。
		:return: 队列长度
		"""
		return len(self.stack)

	def get (self, idx):
		"""
		返回队列中索引对应请求。
		:param idx: 索引值
		:return: 索引对应请求
		"""
		try:
			return self.stack[idx]
		except IndexError:
			return None

	def top (self):
		"""
		返回队列顶端（tick值最小）请求。
		:return: 最老（tick值最小）请求
		"""
		try:
			return self.stack[self.len() - 1]
		except IndexError:
			return None

	def drop (self, reqs):
		"""
		从栈中丢弃请求。
		:param reqs: 支持两种方式：1）进程号；2）请求列表。
		:return: None
		"""
		try:
			if isinstance(reqs, int):
				self.stack = [ r for r in self.stack if r.pid != reqs ]
				del self.rare[reqs]
			else:
				self.stack = [ r for r in self.stack if r not in reqs ]
				# 列表中可能包含rare请求，同时移除
				_pids = set([ r.pid for r in reqs ]).intersection(set(self.rare.keys()))
				for p in _pids:
					del self.rare[p]

				self.debug.dbg("drop: rare %s" % self.rare)
		except KeyError:
			pass

	def rarePids (self):
		"""
		返回所有特殊请求的pid
		:return: pid列表
		"""
		return self.rare.keys()

class ResourceMgr:
	def __init__ (self, positions, capital, debug = False):
		"""
		资源管理器，资金、总持仓位
		:param positions: 仓数
		:param capital: 资金
		:param debug: 打印debug信息
		:return: None
		"""
		self.debug = Debug('ResourceMgr', debug)
		self.positions = positions
		self.capital = capital

	def test (self, pos, cap):
		"""
		测试资源是否足够
		:param pos: 仓数
		:param cap: 资金
		:return: 允许则Ture，否则为False
		"""
		if self.positions - pos < 0 or self.capital - cap < 0:
			return False
		return True

	def alloc (self, pos, cap):
		"""
		分配资源
		:param pos: 仓数
		:param cap: 资金
		:return: 允许则Ture，否则为False
		"""
		self.debug.dbg("alloc: left positions %s, cap %s; alloc pos %s, cap %s" % (
					self.positions, self.capital, pos, cap))
		if not self.test(pos, cap):
			return False

		self.positions -= pos
		self.capital -= cap
		return True

	def free (self, pos, cap):
		"""
		释放资源
		:param pos: 仓数
		:param cap: 资金
		:return: 总是为True
		"""
		self.positions += pos
		self.capital += cap
		self.debug.dbg("free: left positions %s, cap %s; free pos %s, cap %s" % (
					self.positions, self.capital, pos, cap))
		return True

# sched支持的调度命令
EMUL_CA_CMD_CLEAR		= 0
EMUL_CA_CMD_TK_STAT		= 1
EMUL_CA_CMD_REDO_OSP_MP		= 2
EMUL_CA_CMD_WP_MOVE_ON		= 4

class ControlArea(ctypes.Structure):
	"""
	控制合约的共享内存数据结构。各合约单独分配，作为参数传入合约中。
	"""
	_fields_ = [('mode', ctypes.c_int8),		#当前同步点工作状态
		    ('current', ctypes.c_double),	#合约当前已完成tick，执行中的不算
		    ('ack', ctypes.c_double),		#通知合约在到达ack tick后发出确认请求
		    ('command', ctypes.c_uint8),	#调度命令
		    ('tick', ctypes.c_double),		#调度参数，配合command使用
		    ('redo_next', ctypes.c_uint8),	#调度参数，提示合约重做tick后的第一个OSP.OPEN操作
		    ('approve', ctypes.c_uint8),	#调度参数，提示操作是否被允许，主要是WP操作
		    ('nr_np', ctypes.c_uint32),		#记录是否还有NSP.NP消息在队列中
		    ('action', ctypes.c_int8),		#操作类型，配合TK_STAT命令返回参数
		    ('pos', ctypes.c_uint32),		#仓位，配合TK_STAT命令返回参数
		    ('capital', ctypes.c_double)]	#资金，配合TK_STAT命令返回参数

# 发现未识别策略异常
class ExceptionEmulUnknown(Exception):
	pass

# 合约运行状态缓存数据结构（列表）中各部分数据对应的索引。
PS_MP	= 0		#MP控制块
PS_LOCK	= 1		#共享内存保护锁
PS_CTRL	= 2		#共享（内存）控制块
PS_PRI	= 3		#优先级
PS_CONT	= 4		#合约名

class Emulation:
	def __init__ (self, cfg, strategy, debug = False, storeLog = False):
		"""
		模拟交易
		:param cfg: 配置文件
		:param strategy: 策略名
		:param debug: 是否调试
		:param storeLog: 保存合约日志
		"""
		self.debug = Debug('Emulation', debug)	#调试接口
		self.dbgMode = debug
		self.storeLog = storeLog
		#发现未识别策略，提示调用函数处理
		if strategy not in Emulation.validStrategy():
			raise ExceptionEmulUnknown("Found unknown strategy.")
		self.strategy = strategy

		#
		self.testCfg = "%s/%s" % (DEF_EMUL_CONFIG_DIR, cfg)
		self.emuCfg = EmulationConfig(self.testCfg)
		self.contracts = self.emuCfg.getContracts().strip(',').split(',')
		self.startTicks = self.emuCfg.getStartTime().strip(',').split(',')
		self.expireDates = self.emuCfg.getExpireDates().strip(',')
		self.paraLevel = int(self.emuCfg.getParallelLevel())
		# 初始化合约描述接口
		self.descCfg = ContractDescConfig(DEF_CONTRACT_DESC_CFG)
		# sched请求队列
		self.msgQ = mp.Queue()
		# sched请求管理接口
		self.rStack = ReqStack()
		# 合约运行状态缓存数据结构，其中key为进程id
		self.procStates = {}
		# 资源管理接口
		self.resource = ResourceMgr(positions = int(self.emuCfg.getParallelAddMaxAllowed()),
				    	capital = int(self.emuCfg.getParallelCapital()), debug = True)
		# 优先级初始值
		self.priority = 0
		# 日志保存目录
		self.logDir = None

	# 所有支持的策略列表
	@staticmethod
	def validStrategy ():
		ret = ['testfuture']
		return ret

	def __estimateEndTick (self, contract, expireDates):
		"""
		估计合约结束tick
		:param contract: 合约名称
		:param expireDates: 结束日期列表
		:return: 合约结束tick
		"""
		date_in_contract = filter(str.isdigit, contract)
		year = int(date_in_contract[0:2])
		# 合约的实际结束日期应为交割月的上月
		month = int(date_in_contract[2:4])
		if month - 1 == 0:
			year -= 1

		# expireL = expireDates.split(',')
		# 将所有合约到期时间生成以月份为key的字典以加速查找
		# expireMap = dict([(int(ep.split('-')[0]), ep) for ep in expireL])
		expireL = [ep.split(':') for ep in expireDates.split(',')]
		expireMap = dict([(int(ep[0]), ep[1]) for ep in expireL])
		ep = expireMap[month]

		if year < 10:
			ret = "200%s-%s" % (year, ep)
		else:
			ret = "20%s-%s" % (year, ep)

		self.debug.dbg("date_in_contract %s, expire map %s, year %s, month %s, ret %s" % (
					date_in_contract, expireMap, year, month, ret))
		return ret

	def __priorityAssigner (self):
		"""
		分配合约进程优先级。
		:return: 优先级数值。越小优先级越高
		"""
		ret = self.priority
		self.priority += 1
		return ret

	def __setupContractProcess (self, contract, startTick, expireDates, follow = False):
		"""
		启动合约执行
		:param contract: 合约名称
		:param startTick: 开始交易时间
		:param expireDates: 合约结束日期
		:param follow: 跳过startTick，从下一tick开始
		:return: None
		"""
		strategy = None
		if self.strategy == "testfuture":
			import strategy.test_dev
			strategy = strategy.test_dev.TestFuture(contract = contract,
						config = self.descCfg,
						logDir = self.logDir,
						debug = self.dbgMode)

		strategy.setAttrs(maxPosAllowed = int(self.emuCfg.getContractAddMaxAllowed()),
				numPosToAdd = int(self.emuCfg.getContractVolumeAdd()),
				priceVariation = int(self.emuCfg.getContractTriggerLevel()))

		# 启动合约准备，分配共享（内存）控制块、保护锁
		lock = mp.Lock()
		ctrl = mp.Array(ControlArea, [(EMUL_SCHED_MODE_NSP, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)])
		# self.debug.error("ctrl.mode: %s" % ctrl[0].mode)
		p = mp.Process(target = strategy.start, args = (startTick,
					self.__estimateEndTick(contract, expireDates),
					self.msgQ, ctrl[0], lock, self.storeLog, follow))
		p.name = contract
		p.start()
		# 指定优先级
		priority = self.__priorityAssigner()
		self.procStates[p.pid] = [p, lock, ctrl[0], priority, contract]
		self.debug.dbg("__setupContractProcess: new process %s, info %s" % (
							p.pid, self.procStates[p.pid]))

	def __tickReqsHandler (self, wkTick):
		"""
		处理队列中所有wkTick时间发生的请求
		:param wkTick: 目标tick
		:return: 已结束进程id列表
		"""
		# 对tick所对应的请求分类并从队列中行色匆移除待处理
		_alloc = {}
		_free = {}
		_drop = []
		_end = []

		idx = self.rStack.len() - 1
		while idx >= 0:
			r = self.rStack.get(idx)
			if r.tick != wkTick:
				break

			idx -= 1
			_drop.append(r)
			if r.type & EMUL_REQ_END > 0:
				_free[r.pid] = r
				_end.append(r.pid)
			elif r.type & (EMUL_REQ_NSP_CLOSE | EMUL_REQ_OSP_CLOSE) > 0:
				_free[r.pid] = r
			else:
				_alloc[r.pid] = r
		self.rStack.drop(_drop)

		self.debug.error("__tickReqsHandler: _alloc %s, _free %s" % (_alloc, _free))

		# 先释放资源
		for (pid, r) in _free.items():
			self.resource.free(r.pos, r.capital)
			lock = self.procStates[pid][PS_LOCK]
			ctrl = self.procStates[pid][PS_CTRL]
			lock.acquire()
			if r.type & (EMUL_REQ_OSP_CLOSE | EMUL_REQ_END) > 0:
				# OSP.WP得到满足改变状态并继续
				ctrl.mode = EMUL_SCHED_MODE_NSP
				ctrl.command = EMUL_CA_CMD_WP_MOVE_ON
				ctrl.approve = 1
			lock.release()

		# OSP.MP和NSP.WP需要分配资源
		_nspWpPids = _alloc.keys()
		if len(_free):
			# 有仓位释放才需检查OSP.Open是否满足
			_Osp_mp_Nsp_wp = [ (v[PS_PRI], k, _alloc[k] if k in _nspWpPids else None) \
					   for (k, v) in self.procStates.items() \
					   if v[PS_CTRL].mode == EMUL_SCHED_MODE_OSP or k in _nspWpPids ]
		else:
			_Osp_mp_Nsp_wp = [ (v[PS_PRI], k, _alloc[k]) \
					   for (k, v) in self.procStates.items() if k in _nspWpPids ]

		# 需要根据优先级分配资源
		_Osp_mp_Nsp_wp = sorted(_Osp_mp_Nsp_wp, key = lambda x: x[0])
		self.debug.error("__tickReqsHandler: _Osp_mp_Nsp_wp %s" % _Osp_mp_Nsp_wp)

		for (pri, pid, req) in _Osp_mp_Nsp_wp:
			lock = self.procStates[pid][PS_LOCK]
			ctrl = self.procStates[pid][PS_CTRL]
			contract = self.procStates[pid][PS_CONT]
			self.debug.error("__tickReqsHandler: %s: pri %s, pid %s, req %s" % (
								contract, pri, pid, req))
			if req:
				# NSP WP
				approve = self.resource.alloc(req.pos, req.capital)
				lock.acquire()
				# 命令合约进程继续，并通知同步结果
				ctrl.command = EMUL_CA_CMD_WP_MOVE_ON
				(ctrl.mode, ctrl.approve) = (EMUL_SCHED_MODE_NSP, 1) if approve \
								else (EMUL_SCHED_MODE_OSP, 0)
				lock.release()
				self.debug.error("__tickReqsHandler: command %s, approve %s, mode %s" % (
									ctrl.command, approve, ctrl.mode))
			else:
				# OSP MP
				lock.acquire()
				# 命令合约进程返回>=wkTick之前的最近开仓数据
				ctrl.command = EMUL_CA_CMD_TK_STAT
				ctrl.tick = wkTick
				lock.release()
				self.debug.dbg("__tickReqsHandler: %s: wait TK_STAT (%s)" % (contract, wkTick))

				# 等待合约进程完成命令
				while ctrl.command != EMUL_CA_CMD_CLEAR:
					continue

				self.debug.dbg("__tickReqsHandler: %s: TK_STAT: pos %s, capital %s, action %s" % (
								contract, ctrl.pos, ctrl.capital, ctrl.action))

				lock.acquire()
				if ctrl.tick < wkTick:
					if not self.resource.test(ctrl.pos, ctrl.capital):
						# (P2 < pt1, pt1 <= pt3) ==> P2 < pt3
						lock.release()
						self.debug.error("__tickReqsHandler: test resource failed.")
						continue

					# 之前资源满足，不等式不再成立，随后的OSP.OPEN无效
					ctrl.redo_next = 1
					self.debug.error("__tickReqsHandler: %s needs redo next osp.open" % contract)

				elif ctrl.tick == wkTick:
					if not self.resource.alloc(ctrl.pos, ctrl.capital):
						# 当前tick发生OSP.OPEN，但仓位不满足，状态不变；
						lock.release()
						continue

				# 重置OSP进程至OSP.open点
				ctrl.mode = EMUL_SCHED_MODE_NSP
				ctrl.command = EMUL_CA_CMD_REDO_OSP_MP
				ctrl.tick = wkTick
				lock.release()

				# 合约进程操作被重置，OSP.close消息已无意义
				self.rStack.drop(pid)

				# 合约进程环境恢复后会清除命令，一定要确认后再继续，
				# 不然current没有完全恢复会导致ack广播错误
				while ctrl.command != EMUL_CA_CMD_CLEAR:
					continue

		# 返回结束进程id，以便收集状态
		return _end

	def __handleReqs (self):
		"""
		处理请求
		:return: 执行完所有合约返回False，否则返回True
		"""
		start = self.rStack.top().tick
		self.debug.error("__handleReqs: start %s, rStack %s" % (start, self.rStack.stack))
		while True:
			endPids = self.__tickReqsHandler(start)
			self.debug.dbg("__handleReqs: start %s, endPids %s" % (start, endPids))
			for pid in endPids:
				try:
					proc = self.procStates[pid][PS_MP]
					# 等待合约进程正常退出
					proc.join()
					del self.procStates[pid]
					self.debug.dbg("__handleReqs: procStates %s" % self.procStates)
					# 启动新合约，并紧接当前tick从下一tick开始执行，直接从当前tick执行与实际不符。
					self.__setupContractProcess(self.contracts.pop(0),
							    start, self.expireDates, follow = True)
				except KeyError:
					self.debug.error("__handleReqs: received unexpected end req: %d" \
							 		% pid)
					break
				except IndexError:
					# 所有合约已完成且队列中无等待请求，执行结束
					if len(self.procStates) == 0:
						return False
			# time.sleep(0.05)
			top = self.rStack.top()
			if not top or self.__broadcastACK(top):
				return True
			start = top.tick

	def __broadcastACK (self, top, new = None):
		"""
		为请求向各合约进程发送ACK广播，默认为top，如new存在则为new发送。进程在
		当前tick已完成并 >= ack时需向发送ack请求进行确认。如合约在该tick发送
		过调度请求，则认为已确认过并忽略。
		:param top: 目前rStack最老（tick最小）请求
		:param new: 新接受请求
		:return: 等待进程数，0表示所有进程确认完毕，大于0表示还有进程未确认
		"""
		pids = set(self.procStates.keys()) - set([top.pid])
		req = top
		if new:
			pids = set(top.wait.keys()) - set([new.pid])
			req = new

		self.debug.dbg("__broadcastACK: top %s, new %s, pid (all: %s, top: %s, left: %s)" % (
					top, new, self.procStates.keys(), top.wait.keys(), pids))

		req.wait = {}
		for p in pids:
			lock = self.procStates[p][PS_LOCK]
			ctrl = self.procStates[p][PS_CTRL]
			lock.acquire()
			# 除非current >= req.tick并且队列中无NP请求，否则都需要ack确认。
			# current>=0时有可能队列中还有等待请求，所以要求合约进程每发出一个
			# NP请求都要nr_np加1，然后__schedule接受到请求后再减1。
			if ctrl.current >= req.tick and ctrl.nr_np == 0:
				lock.release()
				continue
			else:
				# 当合约进程第一tick就触发开仓（NSP.WP）信号时，current
				# 等于0并且已发送req至队列中，并且不会再发出ack确认，会造成
				# 死锁。该种情况下不能再设置ack确认，应主动检测并规避。
				if p in self.rStack.rarePids():
					self.debug.dbg("__broadcastACK: %s: found rare req" % p)
					lock.release()
					continue

				ctrl.ack = req.tick
				req.wait[p] = 1
			lock.release()

		self.debug.dbg("__broadcastACK: %s: pid %s, wait %s" % (
					self.procStates[req.pid][PS_CONT], req.pid, req.wait))
		return len(req.wait)

	def __rmReqWait (self, dest, req):
		"""
		移除dest中的req对应的等待进程。
		:param dest: 目标请求
		:param req: 待移出（请求对应的）进程id
		:return: 等待进程数
		"""
		self.debug.dbg("__rmReqWait: %s wait %s, req %s" % (
					self.procStates[dest.pid][PS_CONT], dest.wait, req))
		try:
			if req.tick >= dest.tick:
				del dest.wait[req.pid]
		except KeyError:
			pass

		return len(dest.wait)

	def __schedule (self):
		"""
		所有进程的请求调度处理
		:return: None
		"""
		while True:
			req = self.msgQ.get()
			pState = self.procStates[req.pid]
			if req.type & EMUL_REQ_NSP_CLOSE > 0:
				# 见__broadcastACK中解释
				pState[PS_LOCK].acquire()
				pState[PS_CTRL].nr_np -= 1
				pState[PS_LOCK].release()

			top = self.rStack.top()
			self.debug.error("__schedule: req: %s, tick %s, type %s" % (
						pState[PS_CONT], req.tick, req.type))
			if req.mode != pState[PS_CTRL].mode:
				# OSP状态重置为NSP后，现有队列中所有osp req需被丢弃
				continue
			elif req.type == EMUL_REQ_ACK:
				#
				act = self.__rmReqWait(top, req)
			else:
				try:
					# pState[PS_LOCK].acquire()
					_rare = pState[PS_CTRL].current
					# pState[PS_LOCK].release()
					self.rStack.insert(req, _rare == 0)

					self.debug.error("__schedule: req (%s tick %s), top (%s, tick %s)" % (
							pState[PS_CONT], req.tick,
							self.procStates[top.pid][PS_CONT], top.tick))
					if req.tick < top.tick:
						# 有更小的req到达，需要确认同步
						act = self.__broadcastACK(top, req)
					else:
						# 触发req操作
						act = self.__rmReqWait(top, req)
				except AttributeError:
					# top is None
					act = self.__broadcastACK(self.rStack.top())

			if act == 0 and not self.__handleReqs():
				break

	def __initTestEnv(self, argv, name = None):
		"""
		初始化模拟测试环境
		:param argv: 命令参数列表
		:param name: 执行别名
		:return: 成功返回True，否则返回False
		"""
		# 创建测试目录名
		if not name:
			name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

		self.logDir = "%s/%s" % (DEF_TEST_OUT_DIR, name)
		if os.path.exists(self.logDir):
			self.debug.error("'%s' already exists!" % self.logDir)
			return False

		self.debug.dbg("logDir: %s" % self.logDir)
		os.system("mkdir -p %s" % self.logDir)

		# 保存测试配置及命令，以免测试数据对不上
		os.system("cp -f %s %s/EMUL_CONFIG" % (self.testCfg, self.logDir))
		os.system("echo %s > %s/WIN_CMD" % (" ".join(argv), self.logDir))
		return True

	def start (self, argv, name = None):
		"""
		模拟测试入口
		:param argv: 命令参数列表
		:param name: 执行别名
		:return: 成功返回True，否则返回False
		"""
		# 初始化测试环境
		if not self.__initTestEnv(argv, name):
			return False

		try:
			for i in range(self.paraLevel):
				self.__setupContractProcess(self.contracts.pop(0),
					    	self.startTicks[i], self.expireDates)
		except IndexError:
			pass

		# 启动请求调度
		self.__schedule()
		return True

# 测试
def doTest():
	global DEF_EMUL_CONFIG_DIR
	DEF_EMUL_CONFIG_DIR = "../tests"

	testCfg = "%s/test_emul" % DEF_EMUL_CONFIG_DIR
	emul = Emulation(cfg = testCfg,
			 strategy = 'testfuture',
			 dumpName = "test_emul",
			 debug = True)
	emul.start()

if __name__ == '__main__':
	doTest()
