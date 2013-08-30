#-*- coding:utf-8 -*-

import logging
from futures import ApiStruct, MdApi, TraderApi


class Agent(AbsAgent):
    logger = logging.getLogger('ctp.agent')

    def __init__(self,trader,cuser,instruments,strategy_cfg,tday=0,t2order=t2order_if):
        '''
            trader为交易对象
            tday为当前日,为0则为当日
        '''
        AbsAgent.__init__(self)
        ##计时, 用来激发队列
        ##
        self.mdapis = []
        self.trader = trader
        #self.trader.myagent = self
        #if trader != None:
        #    trader.initialize(self)
        self.cuser = cuser
        self.strategy_cfg = strategy_cfg
        self.strategy = strategy_cfg.strategy
        self.t2order = t2order
        self.instruments = c_instrument.create_instruments(instruments,self.strategy,t2order=t2order)
        self.request_id = 1
        self.initialized = False
        self.data_funcs = []  #计算函数集合. 如计算各类指标, 顺序关系非常重要
                              #每一类函数由一对函数组成，.sfunc计算序列用，.func1为动态计算用，只计算当前值
                              #接口为(data), 从data的属性中取数据,并计算另外一些属性
        ###交易
        self.lastupdate = 0
        self.ref2order = {}    #orderref==>order
        #self.queued_orders = []     #因为保证金原因等待发出的指令(合约、策略族、基准价、基准时间(到秒))
        self.front_id = None
        self.session_id = None
        self.order_ref = 1
        self.trading_day = 20110101
        self.scur_day = int(time.strftime('%Y%m%d')) if tday==0 else tday
        #当前资金/持仓
        self.available = 0  #可用资金
        ##查询命令队列
        self.qry_commands = []  #每个元素为查询命令，用于初始化时查询相关数据
        
        #计算函数 sfunc为序列计算函数(用于初始计算), func1为动态计算函数(用于分钟完成时的即时运算)
        self.register_data_funcs(
                BaseObject(sfunc=NFUNC,func1=hreader.time_period_switch),    #时间切换函数
                BaseObject(sfunc=ATR,func1=ATR1),
                BaseObject(sfunc=MA,func1=MA1),
                BaseObject(sfunc=MACD,func1=MACD1),
                BaseObject(sfunc=STREND,func1=STREND1),
            )

        #初始化
        hreader.prepare_directory(instruments)
        self.prepare_data_env()
        #调度器
        self.scheduler = sched.scheduler(time.time, time.sleep)
        #保存锁
        self.lock = threading.Lock()
        #保存分钟数据标志
        self.save_flag = False  #默认不保存

        #actions
        self.actions = []

        self.init_init()    #init中的init,用于子类的处理

        #结算单
        self.isSettlementInfoConfirmed = False  #结算单未确认


    def init_init(self):    #init中的init,用于子类的处理
        pass

    def open_position(self,order):
        ''' 
            发出下单指令
        '''
        req = ApiStruct.InputOrder(
                InstrumentID = order.instrument,
                Direction = order.direction,
                OrderRef = str(order.order_ref),
                LimitPrice = order.price,   #有个疑问，double类型如何保证舍入舍出，在服务器端取整?
                VolumeTotalOriginal = order.volume,
                OrderPriceType = ApiStruct.OPT_LimitPrice,
                
                BrokerID = self.cuser.broker_id,
                InvestorID = self.cuser.investor_id,
                CombOffsetFlag = ApiStruct.OF_Open,         #开仓 5位字符,但是只用到第0位
                CombHedgeFlag = ApiStruct.HF_Speculation,   #投机 5位字符,但是只用到第0位

                VolumeCondition = ApiStruct.VC_AV,
                MinVolume = 1,  #这个作用有点不确定,有的文档设成0了
                ForceCloseReason = ApiStruct.FCC_NotForceClose,
                IsAutoSuspend = 1,
                UserForceClose = 0,
                TimeCondition = ApiStruct.TC_GFD,
            )
        logging.info(u'下单: instrument=%s,方向=%s,数量=%s,价格=%s' % (order.instrument,u'多' if order.direction==ApiStruct.D_Buy else u'空',order.volume,order.price))
        r = self.trader.ReqOrderInsert(req,self.inc_request_id())

    #def close_position(self,order,CombOffsetFlag = ApiStruct.OF_Close): #Close==CloseYesterday
    def close_position(self,order,CombOffsetFlag = ApiStruct.OF_CloseToday):
        ''' 
            发出平仓指令. 默认平今仓
            是平今还是平昨，可以通过order的mytime解决
        '''
        sorder = self.ref2order[order.order_ref].source_order
        sday = sorder.mytime/1000000    #MMDD
        cday = self.scur_day % 10000    #MMDD
        logging.info(u'平仓: sday=%s,cday=%s' % (sday,cday))
        cos_flag = ApiStruct.OF_CloseToday if sday >= cday else ApiStruct.OF_Close    #sday>cday只会在模拟中出现，否则就是穿越了

        req = ApiStruct.InputOrder(
                InstrumentID = order.instrument,
                Direction = order.direction,
                OrderRef = str(order.order_ref),
                LimitPrice = order.price,
                VolumeTotalOriginal = order.volume,
                #CombOffsetFlag = CombOffsetFlag,
                CombOffsetFlag = cos_flag,
                OrderPriceType = ApiStruct.OPT_LimitPrice,
                
                BrokerID = self.cuser.broker_id,
                InvestorID = self.cuser.investor_id,
                CombHedgeFlag = ApiStruct.HF_Speculation,   #投机 5位字符,但是只用到第0位

                VolumeCondition = ApiStruct.VC_AV,
                MinVolume = 1,  #TODO:这个有点不确定. 需要测试确认
                ForceCloseReason = ApiStruct.FCC_NotForceClose,
                IsAutoSuspend = 1,
                UserForceClose = 0,
                TimeCondition = ApiStruct.TC_GFD,
            )
        r = self.trader.ReqOrderInsert(req,self.inc_request_id())

    def cancel_command(self,command):
        '''
            发出撤单指令
        '''
        #print 'in cancel command'
        logging.info(u'A_CC:取消命令')
        req = ApiStruct.InputOrderAction(
                InstrumentID = command.instrument,
                OrderRef = str(command.order_ref),
                BrokerID = self.cuser.broker_id,
                InvestorID = self.cuser.investor_id,
                FrontID = self.front_id,
                SessionID = self.session_id,
                ActionFlag = ApiStruct.AF_Delete,
                #OrderActionRef = self.inc_order_ref()  #没用,不关心这个，每次撤单成功都需要去查资金
            )
        r = self.trader.ReqOrderAction(req,self.inc_request_id())

