# -*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: 2017年 06月 19日 星期一 22:49:45 CST

"""

import sys
sys.path.append("..")
import numpy as np

from datetime import datetime, timedelta
from core.futures import *
from db.tbldesc import *

#
LAST_CUT_TYPE_CL = 0
LAST_CUT_TYPE_SP = 1


class Main(Futures):
    def __init__(self, contract, config, logDir, debug = False):
        """
        采集数据
        :param contract: 合约
        :param config: 合约配置解析接口
        :param logDir: 日志目录
        :param debug: 是否调试
        """
        Futures.__init__(self, contract, config, logDir, debug)
        self.debug = Debug("Discover", debug)
        # tick级统计项目
        self.tkCols = ["OP1_FR", "OP1_SP", "OP2_FR", "OP2_SP", "OP3_FR", "OP3_SP", "OP4_FR", "OP4_SP"]
        # trade级统计项目
        self.trdStatItems = {
            'OP1_FR': ["OP1_OP_TICK", "OP1_OP_PRICE", "OP1_CLS_TICK", "OP1_CLS_PRICE",
                "OP1_FR_Min", "OP1_FR_Max", "OP1_PFR", "OP1_PROFIT", "OP1_FR_DD", "OP1_SP",
                "OP1_FR_Max_TICK", "OP1_FR_Min_TICK", "OP1_SP_FR"],
            'OP2_FR': ["OP2_OP_TICK", "OP2_OP_PRICE", "OP2_CLS_TICK", "OP2_CLS_PRICE",
                "OP2_FR_Min", "OP2_FR_Max", "OP2_PFR", "OP2_PROFIT", "OP2_FR_DD", "OP2_SP",
                "OP2_FR_Max_TICK", "OP2_FR_Min_TICK", "OP2_SP_FR"],
            'OP3_FR': ["OP3_OP_TICK", "OP3_OP_PRICE", "OP3_CLS_TICK", "OP3_CLS_PRICE",
                "OP3_FR_Min", "OP3_FR_Max", "OP3_PFR", "OP3_PROFIT", "OP3_FR_DD", "OP3_SP",
                "OP3_FR_Max_TICK", "OP3_FR_Min_TICK", "OP3_SP_FR"],
            'OP4_FR': ["OP4_OP_TICK", "OP4_OP_PRICE", "OP4_CLS_TICK", "OP4_CLS_PRICE",
                "OP4_FR_Min", "OP4_FR_Max", "OP4_PFR", "OP4_PROFIT", "OP4_FR_DD", "OP4_SP",
                "OP4_FR_Max_TICK", "OP4_FR_Min_TICK", "OP4_SP_FR"],
            }

        self.initStatFrame(tkCols = self.tkCols, trdCols = ["TRD_ID"])
        self.firstTick = self.tickHelper.firstTick()
        # 开仓价备份。如tick内发生平仓操作则会立即从仓位管理队列中移出，这导致在tick结束时
        # 不能统计波动率等指标，故设置了开仓价备份并在统计时优先使用。但在即将进入下一tick
        # 时需确保该备份与仓位管理中完全一致。
        self.opPrice = list()
        #
        self.pLastCut = None
        #
        self.posStatFrame = pd.DataFrame()
        #
        self.dayLastTick = None
        # 入场信号时间
        self.startTrdDays = 1000
        # 退场信号时间
        self.endTrdDays = 1000
        # 加仓参数
        self.apThresholds = []
        # 止损参数
        self.clThresholds = []
        # 止赢参数
        self.spThresholds = ()
        #
        self.posStopProfit = dict()

    def setPosThresholds(self, pos_thresholds):
        """设置仓位控制参数"""
        thresholds = eval(pos_thresholds)
        self.spThresholds = thresholds['stop_profit']
        self.clThresholds = thresholds['cut_loss']
        self.apThresholds = thresholds['add_pos']
        self.startTrdDays = thresholds['start_trade']
        self.endTrdDays = thresholds['end_trade']

    def validSignal(self, tick):
        ret = True
        if tick - self.firstTick < timedelta(days = 10):
            ret = False

        return ret

    def __curFloatRate(self, price, opPrice, direction):
        """
        计算当前浮动利润率
        :param price: 当前价格
        :param direction: 方向
        :param opPrice: 加仓价格
        :return: 浮动利润率|NaN
        """
        ret = np.nan
        if not opPrice:
            return ret

        if direction == SIG_TRADE_LONG:
            ret = (price - opPrice) / opPrice
        elif direction == SIG_TRADE_SHORT:
            ret = (opPrice - price) / opPrice

        return ret

    def storeCustomTickEnv(self, tick, price, direction):
        """
        追加需在tickStatFrame记录的数据，私有变量、统计数据等
        :param tick: 当前tick
        :param price: 当前价格
        :param direction: 方向
        :return: 数据列表
        """
        ret = list()
        # 统计的数据列受trdStatTodo控制
        _maxPos = len(self.trdStatItems)

        for i in range(_maxPos):
            try:
                p = self.opPrice[i]
            except IndexError:
                _pos = self.getPosition(i + 1)
                p = None
                if _pos:
                    p = _pos.price

            _cfr = self.__curFloatRate(price, p, direction)
            #
            _sp = np.nan
            try:
                if self.posStopProfit[i + 1][0]:
                    _sp = self.posStopProfit[i + 1][1]
                    # 每个仓位仅在止赢条件成立tick进行统计
                    self.posStopProfit[i + 1][0] = None
            except KeyError:
                pass
            ret += [_cfr, _sp]

        # tick结束，更新仓位备份，确保与仓位管理中完全一致
        _curPos = self.curPositions()
        if _curPos > len(self.opPrice):
            # 发生加仓，备份中补充新增仓位
            _pos = self.getPosition(_curPos)
            self.opPrice.append(_pos.price)
        elif _curPos < len(self.opPrice):
            # 发生平仓，备份中删除已平仓位
            self.opPrice = self.opPrice[:_curPos]
            # 清理已平仓位的止赢标记
            for p in self.posStopProfit.keys():
                if p > _curPos:
                    del self.posStopProfit[p]

        return ret

    def __genTradeStat(self, direction, col, stCol):
        """
        生成(各仓位的)交易统计数据
        :param direction: 多空方向
        :param col: 目标列
        :param stCol: 统计列
        :return: 统计数据矩阵
        """
        val = self.tickStatFrame[[col]]
        oldIndex = val.index
        val.index = range(len(val))
        # val.to_excel("/tmp/genTradeStat_val.xls")
        nnIdx = set(val[val[col].notnull()].index)
        # 得到有效的数值区间
        _index = val.index
        val.index = list(_index[1:]) + [_index[-1] + 1]
        isnIdx1 = set(val[val[col].isnull()].index)
        val.index = [-1] + list(_index[:-1])
        isnIdx2 = set(val[val[col].isnull()].index)
        val.index = _index
        _ceiling = sorted(list(nnIdx.intersection(isnIdx1)))
        _floor = sorted(list(nnIdx.intersection(isnIdx2)))

        if len(_ceiling) == 0 or len(_floor) == 0:
            # 上沿为空、下沿为空或都为空的情况下数据区间唯一
            todo = [val[val[col].notnull()]]
        else:
            _bound = list()
            if _floor[0] < _ceiling[0]:
                # 第一个数据区间从‘0’索引开始
                _bound.append((0, _floor[0]))
                _floor = _floor[1:]

            if _ceiling[-1] > _floor[-1]:
                # 最后一个数据区间到结束
                _floor += [_index[-1]]

            _bound += zip(_ceiling, _floor)
            todo = map(lambda x: val.iloc[x[0]: x[1]+1], _bound)

        _ret = list()
        for t in todo:
            if t.empty:
                _ret.append([np.nan] * len(stCol))
                continue

            _min = t[col].min()
            _max = t[col].max()
            _tickMin = oldIndex[t[t[col] == t[col].min()].index[0]]
            _tickMax = oldIndex[t[t[col] == t[col].max()].index[0]]
            # 数据区间中的第一个为开仓tick，价格即为开仓价
            _opTick = oldIndex[t.index[0]]
            _endTick = oldIndex[t.index[-1]]
            _opPrice = self.data.getClose(_opTick)
            _endPrice = self.data.getClose(_endTick)
            profit = self.orderProfit(direction, _opPrice, _endPrice)
            pfr = t.iloc[-1][col]
            #
            _spVals = self.tickStatFrame[(self.tickStatFrame.index >= _opTick) & \
                        (self.tickStatFrame.index <= _endTick)]
            _spCol = "%s_SP" % col[0:3]
            _spVals = _spVals[[_spCol]]
            _spVals = _spVals[_spVals[_spCol].notnull()]
            (_spRet, _spFR )= (_spVals.index[0], list(_spVals[_spCol])[0]) if len(_spVals) else (np.nan, np.nan)
            _ret.append([_opTick, _opPrice, _endTick, _endPrice, _min, _max, pfr,
                profit, (pfr - _max), _spRet, _tickMax, _tickMin, _spFR])

        ret = pd.DataFrame(_ret, columns = stCol)
        return ret

    def storeCustomTradeEnv(self, tick, price, direction):
        """
        :param tick: 交易时间
        :param price: 成交价
        :param direction: 多空方向
        :return: 数据列表
        """
        trdID = "%s_%s" % (self.contract, len(self.trdStatFrame) + 1)

        ret = pd.DataFrame()
        for c in sorted(self.trdStatItems.keys()):
            cols = self.trdStatItems[c]
            _ret = self.__genTradeStat(direction, c, cols)
            ret = pd.concat([ret, _ret], axis = 1)

        # 插入交易号
        ret = pd.concat([pd.DataFrame(pd.Series([trdID] * len(ret)), columns=['TRD_ID']), ret], axis = 1)
        #
        self.posStatFrame = self.posStatFrame.append(ret, ignore_index = True)
        # 交易结束，清除所有与本交易相关标记
        self.pLastCut = None
        return [trdID]

    def signalStartTrading(self, tick):
        """
        触发开始交易信号
        :param tick: 交易时间
        :return: SIG_TRADE_SHORT、SIG_TRADE_LONG、None
        """
        ret = None
        if not self.validSignal(tick):
            return ret

        price = self.data.getClose(tick)
        if price < self.data.lowestWithinDays(tick, self.startTrdDays):
            # 20内新低，开空信号
            self.log("%s Hit Short Signal: Close %s, Lowest %s, priceVariation %d" % (
                tick, price, self.data.lowestWithinDays(tick, self.startTrdDays), self.attrs.priceVariation))
            ret = SIG_TRADE_SHORT

        elif price > self.data.highestWithinDays(tick, self.startTrdDays):
            # 20内新高，开多信号
            self.log("%s Hit Long Signal: Close %s, Highest %s, priceVariation %d" % (
                tick, price, self.data.highestWithinDays(tick, self.startTrdDays), self.attrs.priceVariation))
            ret = SIG_TRADE_LONG

        return ret

    def signalEndTrading(self, tick, direction):
        """
        触发结束交易信号
        :param tick: 交易时间
        :param direction: 多空方向
        :return: 触发结束信号返回True，否则返回False
        """
        ret = False
        price = self.data.getClose(tick)

        if direction == SIG_TRADE_SHORT and \
            price > self.data.highestWithinDays(tick, self.endTrdDays):
            # 价格创出10日新高，结束做空
            self.log("	[Short] [%s] Hit Highest in %s days: Clear all!: close %s, highest %d" % (
                        tick, self.endTrdDays, price, self.data.highestWithinDays(tick, self.endTrdDays)))
            ret = True

        elif direction == SIG_TRADE_LONG and \
            price < self.data.lowestWithinDays(tick, self.endTrdDays):
            # 价格创出10日新低，结束做多
            self.log("	[Long] [%s] Hit Lowest in %s days: Clear all!: close %s, lowest %d" % (
                        tick, self.endTrdDays, price, self.data.lowestWithinDays(tick, self.endTrdDays)))
            ret = True

        return ret

    def signalAddPosition(self, tick, direction):
        """
        触发加仓信号
        :param tick: 交易时间
        :param direction: 多空方向
        :return: 触发加仓信号返回True，否则返回False
        """
        ret = False
        try:
            # 当前最高仓位已进入止赢模式，停止加仓（否则止赢模式失效）
            self.posStopProfit[self.curPositions()]
            return ret
        except KeyError:
            pass

        price = self.data.getClose(tick)
        pos = self.getPosition()

        if self.pLastCut:
            _ignore = True
            plc, cutType = self.pLastCut
            # 需保证新开仓价优于最近一次止损价，否则会有止损点无效风险
            if cutType == LAST_CUT_TYPE_CL:
                _ignore = (price <= plc * 1.01) if direction == SIG_TRADE_LONG \
                    else (price >= plc * 0.99)
                if not _ignore:
                    self.debug.dbg("signalAddPosition: [%s] last CL, price %s, plc %s" %(
                        self._signalToDirection(direction), price, plc))
            elif cutType == LAST_CUT_TYPE_SP:
                cfr = self.__curFloatRate(price, plc, direction)
                _thr = self.spThresholds[self.curPositions()][4]
                _ignore = cfr <= _thr
                if not _ignore:
                    self.debug.dbg("signalAddPosition: [%s] last SP, cfr %s, _thr %s" %(
                        self._signalToDirection(direction), cfr, _thr))
            if _ignore:
                return ret

        try:
            _thr = self.apThresholds[self.curPositions()]
            cfr = self.__curFloatRate(price, pos.price, direction)
            # 利润浮动需大于仓位对应阈值，并且需大于该仓位上一次开仓价（否则会导致止损失效）
            if cfr >= _thr:
                self.log("	Add Position: %s, cfr %s" % (tick, cfr))
                ret = True
        except IndexError, e:
            ret = False

        if ret:
            # 止损后才需设置以预防止损失效
            self.pLastCut = None

        return ret

    def signalCutLoss(self, tick, direction):
        """
        触发止损信号
        :param tick: 交易时间
        :param direction: 多空方向
        :return: 未触发止损信号返回False，否则返回自定义参数
        """
        price = self.data.getClose(tick)
        toCut = None
        cfr = list()

        # 从最后一仓开始逆序检查
        posList = list(range(1, self.curPositions() + 1))
        posList.reverse()
        for posIdx in posList:
            pos = self.getPosition(posIdx)
            _cfr = self.__curFloatRate(price, pos.price, direction)
            cfr.append(_cfr)
            try:
                _thr = self.clThresholds[posIdx - 1]
                if _thr is None or _cfr >= _thr:  # 如对应仓位参数为None，则停止止损
                    # 如果不满足则之前仓位也不会满足
                    break
            except IndexError:
                continue  # 对应仓位未指定参数，不止损

            toCut = posIdx
            # 记录止损点，作为加仓条件以避免止损无效
            self.pLastCut = (pos.price, LAST_CUT_TYPE_CL)

        ret = False
        if toCut:
            self.log("	Cut Loss: %s, price %s, cut from %s, cfr %s" % (
                        tick, price, toCut, cfr))
            ret = [toCut]

        return ret

    def tradeCutLoss(self, tick, direction, args):
        """
        止损。必须被重载实现
        @MUST_OVERRIDE
        :param tick: 交易时间
        :param direction: 方向
        :param args: 自定义参数
        :return: 成功返回True，否则返回False
        """
        toCut = args[0]
        price = self.data.getClose(tick)
        nrPos = self.curPositions() - toCut + 1
        ret = self.closePositions(tick, price, direction, nrPos, reverse = True)
        return ret

    def __couldStopProfit(self, price, pos, espType, thrSP, direction):
        """
        是否能够止赢
        :param price: 当前价
        :param pos: 持仓
        :param espType: esp类型，1或2
        :param thrSP: 止赢阈值
        :param direction: 多空方向
        :return: 能返回True，否则返回False
        """
        ret = False
        if not espType or not thrSP:
            return ret

        cfr = self.__curFloatRate(price, pos.price, direction)
        if (espType == 1 and cfr >= thrSP) or (espType == 2 and cfr > 0):
            self.debug.dbg("__couldStopProfit: signal %s, price (pos %s, cur %s), esp %s, thrSP %s" % (
                    self._signalToDirection(direction), pos.price, price, espType,
                    thrSP if espType == 1 else 0))
            ret = True
        return ret

    def signalStopProfit(self, tick, direction):
        """
        触发止赢信号
        :param tick: 交易时间
        :param direction: 多空方向
        :return: 未触发止损信号返回False，否则返回自定义参数
        """
        ret = False

        if not self.dayLastTick or self.dayLastTick.date() != tick.date():
            self.dayLastTick = self.tickHelper.dayLastTick(tick)

        price = self.data.getClose(tick)
        toSP = None
        _skipSP = False

        # 从最后一仓开始逆序检查
        posList = list(range(1, self.curPositions() + 1))
        posList.reverse()
        maxUndefPos = None
        for posIdx in posList:
            pos = self.getPosition(posIdx)
            try:
                (thrDL, thrESP1, thrESP2, thrSP) = self.spThresholds[posIdx - 1][0:4]
            except (IndexError, ValueError):
                if not maxUndefPos:
                    maxUndefPos = posIdx
                continue  # 对应仓位未指定参数或参数为空，则不止赢

            try:
                espType = self.posStopProfit[posIdx][2]
                # 更高的仓位未设上赢，则低仓位也不能止赢
                if maxUndefPos and maxUndefPos > posIdx:
                    continue
                if not _skipSP and self.__couldStopProfit(price, pos, espType, thrSP, direction):
                    toSP = posIdx
                    self.pLastCut = (pos.price, LAST_CUT_TYPE_SP)
                else:
                    # 不允许隔仓SP，否则仓位统计会发生混乱
                    _skipSP = True
            except KeyError:
                # 该仓没有ESP，以下仓位由于隔仓不允许SP
                _skipSP = True
                if tick != self.dayLastTick:
                    # 仅在交易日的最后一个tick检查是否触发ESP
                    break

                if toSP:
                    # 高仓位已经触发止赢，价格必然高于低仓位，ESP条件不可能成立
                    break

                if not thrDL:
                    # 为了避免仓位混乱，除第一个仓位外都必须设置SP相关参数，否则引起仓位混乱
                    break

                espType = 1
                _fr = self.__curFloatRate(price, pos.price, direction)
                if _fr > thrESP1:
                    # 低仓位ESP条件仍有可能满足
                    continue
                elif _fr < thrESP2:
                    espType = 2

                _dayLasts = self.tickHelper.dayLasts(pos.time, tick)
                if _dayLasts < thrDL:
                    #
                    continue

                self.debug.dbg("signalStopProfit: pos %s, cur (tick %s, price %s), DL %s, FR %s, esp %s" % (
                    posIdx, tick, price, _dayLasts, _fr, espType))
                #
                self.posStopProfit[posIdx] = [True, _fr, espType]

        if toSP:
            ret = [toSP]
        return ret

    def tradeStopProfit(self, tick, direction, args):
        """
        止赢。必须被重载实现
        @MUST_OVERRIDE
        :param tick: 交易时间
        :param direction: 方向
        :param args: 自定义参数
        :return: 成功返回True，否则返回False
        """
        toCut = args[0]
        price = self.data.getClose(tick)
        self.log("	Stop Profit: %s, price %s, stop from %s" % (tick, price, toCut))
        nrPos = self.curPositions() - toCut + 1
        ret = self.closePositions(tick, price, direction, nrPos, reverse = True)
        return ret

    def customExit(self):
        """

        :return: None
        """
        # 将tick数据以excel格式保存
        _data = "%s/%s" % (self.logDir, self.contract)
        self.posStatFrame.to_excel("%s_POS_STAT.xlsx" % _data, float_format = "%.5f")
