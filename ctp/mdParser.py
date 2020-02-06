# -*- coding:utf-8 -*-

"""
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>
Start: Tue Nov 19 23:16:10 CST 2019

"""

import os
import sys
sys.path.append('..')
import signal
import time
import traceback
import select
import socket
import logging
import re
import multiprocessing as mp
from datetime import datetime
from dateutil.relativedelta import relativedelta

import ctpagent
import ctp.futconfig as futconfig
import core.corecfg as corecfg


class MdProc:
    """

    """
    def __init__(self, mp, pid):
        self.mp = mp
        self.pid = pid


class MarketDataLauncher(object):
    """

    """
    #
    CFG_FILE = os.path.join(os.environ.get('HOME'), '.winning', 'config')

    def __init__(self):
        #
        self.gCfg = corecfg.GlobalConfig(MarketDataLauncher.CFG_FILE)
        self.logDir = os.path.join(self.gCfg.getLogDir(), 'market_data')
        if not os.path.exists(self.logDir):
            os.mkdir(self.logDir)
        #
        self.fCfg = futconfig.CtpConfig(MarketDataLauncher.CFG_FILE)
        self.workDir = self.fCfg.getDataDir('MarketData')
        if not os.path.exists(self.workDir):
            os.mkdir(self.workDir)
        #
        self.logger = None
        #
        self.wkMdp = {}
        #
        self.insToFps = {}
        #
        self.mainThrExit = False
        self.daemonGoExit = False
        #
        self.agent = None
        self.dispatchInProgress = False

    @classmethod
    def makeLogger(cls, name, level, filename, format=None):
        """
        New and initialized a new logger instance.
        :param level:
        :param filename:
        :param format:
        :return: an initialized logger
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        fh = logging.FileHandler(filename)
        fh.setFormatter(logging.Formatter(format))
        logger.addHandler(fh)
        return logger

    def workerMsgRsp(self, fd):
        pass

    def __workerExit(self):
        """

        """
        for k, v in self.insToFps:
            fp = v['fp']
            if fp:
                fp.close()

    def rtnDepthMarketDataRsp(self, depth_market_data):
        """

        :param depth_market_data:
        """
        dp = depth_market_data
        try:
            if dp.LastPrice > 999999 or dp.LastPrice < 10:
                self.logger.warning(u'收到的行情数据有误:%s,LastPrice=:%s' % (
                    dp.InstrumentID, dp.LastPrice))
            if dp.InstrumentID not in self.instruments:
                self.logger.warning(u'收到未订阅的行情:%s' % dp.InstrumentID)
                return

            # print(u'[%s]，[价：最新/%g，买/%g，卖/%g], [量：买/%d，卖/%d，总：%d], [最高/%d，最低/%d], 时间：%s' % (
            # 	dp.InstrumentID, dp.LastPrice, dp.BidPrice1, dp.AskPrice1, dp.BidVolume1, dp.AskVolume1,
            # 	dp.Volume, dp.HighestPrice, dp.LowestPrice, dp.UpdateTime))
            fp = self.insToFps[dp.InstrumentID]['fp']
            fp.write(depth_market_data)
        except Exception, e:
            self.logger.debug(u'接收行情数据异常! : \n%s' % (traceback.format_exc(e)))

    def mdWorker(self, instruments, fdw, wkdir):
        """

        :param instruments:
        :param fdw:
        :param wkdir:
        :return:
        """
        ret = 0
        self.logger = MarketDataLauncher.makeLogger('worker', logging.DEBUG,
                        os.path.join(self.logDir, 'worker-%s' % os.getpid()),
                        '%(asctime)s:%(name)s:%(funcName)s:%(lineno)d: <%(levelname)s> %(message)s')

        try:
            # Create file to store each instrument's data.
            self.insToFps = dict()
            for i in instruments:
                _file = os.path.join(wkdir, i)
                fp = open(_file, 'a')
                self.insToFps[i] = {'fp': fp}

            # Init agent and start receiving market data.
            agent = ctpagent.MarketDataAgent(self.fCfg.getBrokerid('MarketData'),
                         self.fCfg.getInvestor('MarketData'), self.fCfg.getPasswd('MarketData'),
                         self.fCfg.getServer('MarketData'))
            agent.init_init(self.logger, self.rtnDepthMarketDataRsp)
            agent.subscribe(instruments)
        except Exception, e:
            self.logger.error("Failed to init agent: \n%s", traceback.format_exc(e))
            self.__workerExit()
            ret = 1
            sys.exit(ret)

        while 1:
            rs, ws, es = select.select([fdw], [], [fdw], 0.5)
            ret = self.workerMsgRsp(rs)
            if ret:
                break

        agent.release()
        self.__workerExit()
        sys.exit(ret)

    def mainSigHandler(self, sig, frame):
        """

        :param sig:
        :param frame:
        """
        self.mainThrExit = True

    def daemonSigHandler(self, sig, frame):
        """
        Signal handler for daemon process.
        :param sig:
        :param frame:
        """
        self.logger.warn('Received signal %s' % sig)
        self.daemonGoExit = True

    def daemonMsgRsp(self, frd, mdp):
        """

        :param frd:
        :param mdp:
        :return:
        """
        pass

    def stopWorkers(self):
        pass

    def consoleHandler(self, fd_sock):
        """

        :param fd_sock:
        :return:
        """
        pass

    def setupConsole(self):
        pass

    def __dispatch(self, instruments, jobs, tradingDay):
        """

        :param instruments:
        :param jobs:
        :param tradingDay:
        :return: 0|1
        """
        ret = 1
        # Convert passed patterns to real instruments code.
        instruments = self.buildInstruments(instruments)
        if not instruments:
            self.logger.error("Can not build invalid instruments, exit!")
            return ret

        try:
            # Create a directory to store the received data.
            workDir = os.path.join(self.workDir, tradingDay)
            if not os.path.exists(workDir):
                os.mkdir(workDir)
        except OSError, e:
            self.logger.error("Failed to create data directory:\n%s" % traceback.format_exc(e))
            return ret

        #
        nr = len(instruments.keys()) / jobs + 1
        for i in range(jobs):
            _instruments = []
            for k in instruments.keys()[i*nr:(i+1)*nr]:
                _instruments += list(instruments[k])
            rd, wr = mp.Pipe()
            _proc = mp.Process(target=self.mdWorker, args=(_instruments, wr, workDir))
            _proc.start()
            mdp = MdProc(_proc, _proc.pid)
            self.wkMdp[rd] = mdp

        if len(self.wkMdp):
            ret = 0
        return ret

    def __validSignal(self):
        """

        :return:
        """
        ret = None
        if self.dispatchInProgress:
            return ret

        try:
            if not self.agent:
                self.agent = ctpagent.MarketDataAgent(self.fCfg.getBrokerid('MarketData'),
                             self.fCfg.getInvestor('MarketData'), self.fCfg.getPasswd('MarketData'),
                             self.fCfg.getServer('MarketData'))
                self.agent.init_init()
            _ret = self.agent.getTradingDay()
            if _ret != '19800101':
                ret = _ret
        except Exception, e:
            self.logger.error("Error to determine the signal to dispatch: %s\n" % traceback.format_exc(e))

        return ret

    def launch(self, instruments, jobs):
        """

        :param instruments:
        :param jobs:
        :return:
        """
        ret = 0
        # From now on, child will be using its own debug logger.
        self.logger = MarketDataLauncher.makeLogger('daemon', logging.DEBUG,
                        os.path.join(self.logDir, 'daemon-%s' % os.getpid()),
                        '%(asctime)s:%(name)s:%(funcName)s:%(lineno)d: <%(levelname)s> %(message)s')

        # Daemon will exit if received SIGUSR1 signal.
        signal.signal(signal.SIGUSR1, self.daemonSigHandler)
        # Notify the Main to exit.
        ppid = os.getppid()
        os.kill(ppid, signal.SIGUSR1)

        #
        fdc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fdc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        fdc.bind(('127.0.0.1', 9900))
        fdc.listen(10)

        while 1:
            tradingDay = self.__validSignal()
            if self.daemonGoExit:
                # Received the signal from user to exit daemon.
                break
            elif tradingDay:
                if self.__dispatch(instruments, jobs, tradingDay):
                    self.logger.error("Failed to dispatch workers.")
                    ret = 1
                    break
                self.dispatchInProgress = True
            else:
                time.sleep(1)
                rfds = self.wkMdp.keys() + [fdc]
                rs, ws, es = select.select(rfds, [], rfds, 0.5)
                for r in rs:
                    if r == fdc:
                        self.consoleHandler(r)
                    else:
                        self.daemonMsgRsp(r, self.wkMdp[r])

        fdc.close()
        self.stopWorkers()
        if self.agent:
            self.agent.release()
        sys.exit(ret)

    def __buildInstruments(self, instrument, pattern=None):
        """

        :param instrument:
        :param pattern:
        :return: a list of instruments matching pattern if specified.
        """
        ret = []
        if pattern:
            pattern = pattern.replace('*', '\d+') + '$'

        for i in range(1, 13):
            _time = datetime.now() + relativedelta(months=i)
            _insId = instrument + datetime.strftime(_time, "%y%m")
            if not pattern or re.search(pattern, _insId):
                ret.append(_insId)

        return ret

    def printInstances(self):
        pass

    def buildInstruments(self, patterns):
        """
        Build the instruments list for which to receive market data.
        :param patterns:
        :return: None if found error, otherwise return a dict
        """
        ret = {}

        patterns = patterns.split(',')
        for p in patterns:
            _instrument = re.search('[a-z]{1,2}', p).group()
            if re.search('^[a-z]{1,2}$', p):
                # i.e. 'FG'
                _ret = self.__buildInstruments(p)
            elif re.search('^[a-z]{1,2}\d{4}$', p):
                # i.e. 'FG2001'
                _ret = [p]
            elif re.search('^[a-z]{1,2}((\d{0,3}\*)|(\d{0,2}\*\d)|(\d{0,1}\*\d{2})|(\*\d{3}))$', p):
                # such as 'FG*', 'FG19*', 'FG1*01', 'FG*01', etc
                _ret = self.__buildInstruments(_instrument, p)
            else:
                print("Failed to build instruments for pattern '%s'." % p)
                ret = None
                break

            if _instrument not in ret.keys():
                ret[_instrument] = set(_ret)
            else:
                ret[_instrument].update(set(_ret))

        return ret

    def optionsHandler(self, options, args):
        """
        Handler for passed commands.
        :return: 0|1
        """
        ret = 0

        if options.select:
            jobs = 1
            if options.jobs:
                jobs = int(options.jobs)

            child = os.fork()
            if child == 0:
                # In child's context, expect child would never return.
                self.launch(options.select, jobs)

            # In parent's context.
            try:
                signal.signal(signal.SIGUSR1, self.mainSigHandler)
                # Wait until receive child's signal.
                while not self.mainThrExit:
                    time.sleep(1)
                    continue
            except KeyboardInterrupt, e:
                os.kill(child, signal.SIGUSR1)
                ret = 1
                return ret

        if options.list:
            self.printInstances()

        if options.console:
            self.setupConsole()

        return ret


def optionParser(parser):
    """
    Entry to parse commands.
    :param parser: And OptionParser object
    """
    parser.add_option('-s', '--select', dest='select',
        help="Specify a list of Future code or abbreviations.")
    parser.add_option('-l', '--list', action="store_true", dest='list',
        help="List all active md daemons in background.")
    parser.add_option('-j', '--jobs', dest='jobs',
        help="Number of jobs to receive md data.")
    parser.add_option('-c', '--console', dest='console',
        help="Login on a daemon's console.")
    parser.add_option('-D', '--debug', action="store_true", dest='debug',
        help="Enable debug mode.")

    (options, args) = parser.parse_args()
    mdl = MarketDataLauncher()
    return mdl.optionsHandler(options, args)
