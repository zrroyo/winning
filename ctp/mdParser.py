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

import misc.debug
import ctpagent
import ctp.futconfig as futconfig


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
    CTP_CFG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'real.ini')

    def __init__(self):
        self.logger = None
        self.workDir = None
        #
        self.wkMdp = {}
        #
        self.mainThrExit = False
        #
        self.__insToFps = {}
        #
        self.workerGoExit = True
        self.daemonGoExit = False

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

    def workerSigHandler(self, sig):
        """

        :param sig:
        """
        self.logger.warn('Received signal %s' % sig)
        self.workerGoExit = True

    def workerMsgRsp(self, fd):
        pass

    def workerExit(self, status):
        """

        """
        for k, v in self.__insToFps:
            fp = v['fp']
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
            fp = self.__insToFps[dp.InstrumentID]['fp']
            fp.write(depth_market_data)
        except Exception, e:
            self.logger.debug(u'接收行情数据异常! : \n%s' % (traceback.format_exc(e)))

    def mdWorker(self, instruments, fdw):
        """

        :param instruments:
        :param fdw:
        :return:
        """
        ret = 0
        self.logger = MarketDataLauncher.makeLogger('worker', logging.DEBUG, 'worker-%s' % os.getpid(),
                        '%(asctime)s:%(name)s:%(funcName)s:%(lineno)d: <%(levelname)s> %(message)s')
        #
        signal.signal(signal.SIGKILL, self.workerSigHandler)
        signal.signal(signal.SIGTERM, self.workerSigHandler)

        # Create file to store each instrument's data.
        self.__insToFps = dict()
        for i in instruments:
            try:
                fp = open(os.path.join(self.workDir, i), 'a')
                self.__insToFps[i] = {'fp': fp}
            except IOError, e:
                self.logger.error("Failed to open data file for %s, due to:\n%s" % (i, traceback.format_exc(e)))
                ret = 1
                # Need notify the control-thread.
                return ret

        # Start market data agent to receive data.
        cfg = futconfig.CtpConfig(MarketDataLauncher.CTP_CFG_FILE)
        agent = ctpagent.MarketDataAgent(instruments, cfg.getBrokerid('MarketData'),
                     cfg.getInvestor('MarketData'), cfg.getPasswd('MarketData'), cfg.getServer('MarketData'))
        agent.init_init(self.logger, self.rtnDepthMarketDataRsp)

        while 1:
            rs, ws, es = select.select([fdw], None, [fdw], timeout=0.5)
            if self.workerMsgRsp(rs) != 0:
                ret = 1
                break

            if self.workerGoExit:
                break

        self.workerExit(ret)

    def mainSigHandler(self, sig):
        """

        :param sig:
        :return:
        """
        self.mainThrExit = True

    def daemonSigHandler(self, sig):
        """
        Signal handler for daemon process.
        :param sig:
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

    def launch(self, instruments, jobs):
        """

        :param instruments:
        :param jobs:
        :return:
        """
        ppid = os.getpid()
        pid = os.fork()
        if pid:
            # In parent's context.
            ret = 0
            try:
                signal.signal(signal.SIGUSR1, self.mainSigHandler)
                # Wait until receive child's signal.
                while not self.mainThrExit:
                    time.sleep(1)
                    continue
            except KeyboardInterrupt, e:
                os.kill(pid, signal.SIGKILL)
                ret = 1
            return ret

        # In child's context.
        # From now on, child will be using its own debug logger.
        self.logger = MarketDataLauncher.makeLogger('daemon', logging.DEBUG, 'daemon-%s' % os.getpid(),
                        '%(asctime)s:%(name)s:%(funcName)s:%(lineno)d: <%(levelname)s> %(message)s')

        signal.signal(signal.SIGKILL, self.daemonSigHandler)

        #
        nr = len(instruments.keys()) / jobs + 1
        for i in range(jobs):
            _instruments = [instruments[k] for k in instruments.keys()[i*nr:(i+1)*nr]]
            rd, wr = mp.Pipe()
            _proc = mp.Process(target=self.mdWorker, args=(_instruments, wr))
            _proc.start()
            mdp = MdProc(_proc, _proc.pid)
            self.wkMdp[rd] = mdp

        try:
            # Parent may exit now.
            os.kill(ppid, signal.SIGUSR1)
        except OSError, e:
            self.logger.error('Parent %s seems not existing any more, start exiting!' % ppid)
            self.stopWorkers()
            sys.exit(1)

        #
        fdc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fdc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        fdc.bind(('127.0.0.1', 9900))
        fdc.listen(10)
        # rlist.append(fdc)

        while 1:
            # Have received the exit signal.
            if self.daemonGoExit:
                break

            rlist = self.wkMdp.keys()
            rs, ws, es = select.select(rlist, None, rlist, timeout=0.5)
            for r in rs:
                if r == fdc:
                    self.consoleHandler(r)
                else:
                    self.daemonMsgRsp(r, self.wkMdp[r])

        # Daemon exit.
        fdc.close()
        self.stopWorkers()
        sys.exit(1)

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
            _instrment = re.search('[A-Z]{1,2}', p).group()
            if re.search('^[A-Z]{1,2}$', p):
                # i.e. 'FG'
                _ret = self.__buildInstruments(p)
            elif re.search('^[A-Z]{1,2}\d{4}$', p):
                # i.e. 'FG2001'
                _ret = [p]
            elif re.search('^[A-Z]{1,2}((\d{0,3}\*)|(\d{0,2}\*\d)|(\d{0,1}\*\d{2})|(\*\d{3}))$', p):
                # such as 'FG*', 'FG19*', 'FG1*01', 'FG*01', etc
                _ret = self.__buildInstruments(_instrment, p)
            else:
                print("Failed to build instruments for pattern '%s'." % p)
                ret = None
                break

            if _instrment not in ret.keys():
                ret[_instrment] = set(_ret)
            else:
                ret[_instrment].update(set(_ret))

        return ret

    def optionsHandler(self, options, args):
        """
        Handler for passed commands.
        :return: 0|1
        """
        ret = 1

        if options.select:
            instruments = self.buildInstruments(options.select)
            if not instruments:
                return ret

            jobs = 1
            if options.jobs:
                jobs = int(options.jobs)

            if self.launch(instruments, jobs):
                return ret

        if options.list:
            self.printInstances()

        if options.console:
            self.setupConsole()

        ret = 0
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
