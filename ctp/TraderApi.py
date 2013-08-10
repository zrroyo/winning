#-*- coding=utf-8 -*-
"""

A wrapper for CTP's Api library
author: Lvsoft@gmail.com
date: 2010-07-20

This file is part of python-ctp library

python-ctp is free software; you can redistribute it and/or modify it
under the terms of the GUL Lesser General Public License as published
by the Free Software Foundation; either version 2.1 of the License, or
(at your option) any later version.

python-ctp is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY of FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along the python-ctp; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301 USA
"""

import _ctp_Trader
import os
import UserApiStruct

_ctp_Trader.register_struct(UserApiStruct)

class TraderSpi:
    def register_api(self, api):
        self.api=api

    def OnRtnChangeAccountByBank(self, pChangeAccount):
        '''���з����������˺�֪ͨ'''
        pass

    def OnRspQryInstrument(self, pInstrument, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ��Լ��Ӧ'''
        pass

    def OnErrRtnFutureToBankByFuture(self, pReqTransfer, pRspInfo):
        '''�ڻ������ڻ��ʽ�ת���д���ر�'''
        pass

    def OnRspQryInstrumentMarginRate(self, pInstrumentMarginRate, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ��Լ��֤������Ӧ'''
        pass

    def OnFrontDisconnected(self, nReason):
        '''���ͻ����뽻�׺�̨ͨ�����ӶϿ�ʱ���÷��������á���������������API���Զ��������ӣ��ͻ��˿ɲ�������
@param nReason ����ԭ��
        0x1001 �����ʧ��
        0x1002 ����дʧ��
        0x2001 ����������ʱ
        0x2002 ��������ʧ��
        0x2003 �յ�������'''
        pass

    def OnRspQryExchange(self, pExchange, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ��������Ӧ'''
        pass

    def OnRspOrderAction(self, pInputOrderAction, pRspInfo, nRequestID, bIsLast):
        '''��������������Ӧ'''
        pass

    def OnErrRtnRepealBankToFutureByFutureManual(self, pReqRepeal, pRspInfo):
        '''ϵͳ����ʱ�ڻ����ֹ������������ת�ڻ�����ر�'''
        pass

    def OnErrRtnBankToFutureByFuture(self, pReqTransfer, pRspInfo):
        '''�ڻ����������ʽ�ת�ڻ�����ر�'''
        pass

    def OnRtnFromFutureToBankByBank(self, pRspTransfer):
        '''���з����ڻ��ʽ�ת����֪ͨ'''
        pass

    def OnRspQryInvestor(self, pInvestor, pRspInfo, nRequestID, bIsLast):
        '''�����ѯͶ������Ӧ'''
        pass

    def OnRspRemoveParkedOrder(self, pRemoveParkedOrder, pRspInfo, nRequestID, bIsLast):
        '''ɾ��Ԥ����Ӧ'''
        pass

    def OnRspQryTransferBank(self, pTransferBank, pRspInfo, nRequestID, bIsLast):
        '''�����ѯת��������Ӧ'''
        pass

    def OnRspQryBrokerTradingAlgos(self, pBrokerTradingAlgos, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ���͹�˾�����㷨��Ӧ'''
        pass

    def OnRspQrySettlementInfo(self, pSettlementInfo, pRspInfo, nRequestID, bIsLast):
        '''�����ѯͶ���߽�������Ӧ'''
        pass

    def OnRtnRepealFromFutureToBankByBank(self, pRspRepeal):
        '''���з�������ڻ�ת����֪ͨ'''
        pass

    def OnRtnOpenAccountByBank(self, pOpenAccount):
        '''���з������ڿ���֪ͨ'''
        pass

    def OnRspError(self, pRspInfo, nRequestID, bIsLast):
        '''����Ӧ��'''
        pass

    def OnRspQryCFMMCTradingAccountKey(self, pCFMMCTradingAccountKey, pRspInfo, nRequestID, bIsLast):
        '''��ѯ��֤����ϵͳ���͹�˾�ʽ��˻���Կ��Ӧ'''
        pass

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        '''��¼������Ӧ'''
        pass

    def OnRtnRepealFromFutureToBankByFuture(self, pRspRepeal):
        '''�ڻ���������ڻ�ת�����������д�����Ϻ��̷��ص�֪ͨ'''
        pass

    def OnRspParkedOrderAction(self, pParkedOrderAction, pRspInfo, nRequestID, bIsLast):
        '''Ԥ�񳷵�¼��������Ӧ'''
        pass

    def OnErrRtnOrderAction(self, pOrderAction, pRspInfo):
        '''������������ر�'''
        pass

    def OnRtnCancelAccountByBank(self, pCancelAccount):
        '''���з�����������֪ͨ'''
        pass

    def OnRtnInstrumentStatus(self, pInstrumentStatus):
        '''��Լ����״̬֪ͨ'''
        pass

    def OnRspQryContractBank(self, pContractBank, pRspInfo, nRequestID, bIsLast):
        '''�����ѯǩԼ������Ӧ'''
        pass

    def OnRspOrderInsert(self, pInputOrder, pRspInfo, nRequestID, bIsLast):
        '''����¼��������Ӧ'''
        pass

    def OnRspQryEWarrantOffset(self, pEWarrantOffset, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ�ֵ��۵���Ϣ��Ӧ'''
        pass

    def OnRspUserPasswordUpdate(self, pUserPasswordUpdate, pRspInfo, nRequestID, bIsLast):
        '''�û��������������Ӧ'''
        pass

    def OnRspParkedOrderInsert(self, pParkedOrder, pRspInfo, nRequestID, bIsLast):
        '''Ԥ��¼��������Ӧ'''
        pass

    def OnRtnTradingNotice(self, pTradingNoticeInfo):
        '''����֪ͨ'''
        pass

    def OnRspFromBankToFutureByFuture(self, pReqTransfer, pRspInfo, nRequestID, bIsLast):
        '''�ڻ����������ʽ�ת�ڻ�Ӧ��'''
        pass

    def OnRspQryInvestorPositionCombineDetail(self, pInvestorPositionCombineDetail, pRspInfo, nRequestID, bIsLast):
        '''�����ѯͶ���ֲ߳���ϸ��Ӧ'''
        pass

    def OnRspFromFutureToBankByFuture(self, pReqTransfer, pRspInfo, nRequestID, bIsLast):
        '''�ڻ������ڻ��ʽ�ת����Ӧ��'''
        pass

    def OnHeartBeatWarning(self, nTimeLapse):
        '''������ʱ���档����ʱ��δ�յ�����ʱ���÷��������á�
@param nTimeLapse �����ϴν��ձ��ĵ�ʱ��'''
        pass

    def OnErrRtnQueryBankBalanceByFuture(self, pReqQueryAccount, pRspInfo):
        '''�ڻ������ѯ����������ر�'''
        pass

    def OnRspQryAccountregister(self, pAccountregister, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ����ǩԼ��ϵ��Ӧ'''
        pass

    def OnRspQryTradingCode(self, pTradingCode, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ���ױ�����Ӧ'''
        pass

    def OnRtnErrorConditionalOrder(self, pErrorConditionalOrder):
        '''��ʾ������У�����'''
        pass

    def OnRtnFromBankToFutureByFuture(self, pRspTransfer):
        '''�ڻ����������ʽ�ת�ڻ�֪ͨ'''
        pass

    def OnRspQrySettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ������Ϣȷ����Ӧ'''
        pass

    def OnRtnQueryBankBalanceByFuture(self, pNotifyQueryAccount):
        '''�ڻ������ѯ�������֪ͨ'''
        pass

    def OnRtnOrder(self, pOrder):
        '''����֪ͨ'''
        pass

    def OnRspQryTransferSerial(self, pTransferSerial, pRspInfo, nRequestID, bIsLast):
        '''�����ѯת����ˮ��Ӧ'''
        pass

    def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
        '''�����ѯͶ���ֲ߳���Ӧ'''
        pass

    def OnRspUserLogout(self, pUserLogout, pRspInfo, nRequestID, bIsLast):
        '''�ǳ�������Ӧ'''
        pass

    def OnErrRtnRepealFutureToBankByFutureManual(self, pReqRepeal, pRspInfo):
        '''ϵͳ����ʱ�ڻ����ֹ���������ڻ�ת���д���ر�'''
        pass

    def OnRspQryInvestorPositionDetail(self, pInvestorPositionDetail, pRspInfo, nRequestID, bIsLast):
        '''�����ѯͶ���ֲ߳���ϸ��Ӧ'''
        pass

    def OnRtnFromBankToFutureByBank(self, pRspTransfer):
        '''���з��������ʽ�ת�ڻ�֪ͨ'''
        pass

    def OnRspQryParkedOrderAction(self, pParkedOrderAction, pRspInfo, nRequestID, bIsLast):
        '''�����ѯԤ�񳷵���Ӧ'''
        pass

    def OnRspQryBrokerTradingParams(self, pBrokerTradingParams, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ���͹�˾���ײ�����Ӧ'''
        pass

    def OnRspQryParkedOrder(self, pParkedOrder, pRspInfo, nRequestID, bIsLast):
        '''�����ѯԤ����Ӧ'''
        pass

    def OnRspQueryBankAccountMoneyByFuture(self, pReqQueryAccount, pRspInfo, nRequestID, bIsLast):
        '''�ڻ������ѯ�������Ӧ��'''
        pass

    def OnRspQueryMaxOrderVolume(self, pQueryMaxOrderVolume, pRspInfo, nRequestID, bIsLast):
        '''��ѯ��󱨵�������Ӧ'''
        pass

    def OnRtnTrade(self, pTrade):
        '''�ɽ�֪ͨ'''
        pass

    def OnErrRtnOrderInsert(self, pInputOrder, pRspInfo):
        '''����¼�����ر�'''
        pass

    def OnRspQryTradingNotice(self, pTradingNotice, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ����֪ͨ��Ӧ'''
        pass

    def OnRtnRepealFromBankToFutureByFuture(self, pRspRepeal):
        '''�ڻ������������ת�ڻ��������д�����Ϻ��̷��ص�֪ͨ'''
        pass

    def OnRspQryNotice(self, pNotice, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ�ͻ�֪ͨ��Ӧ'''
        pass

    def OnRspQryTradingAccount(self, pTradingAccount, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ�ʽ��˻���Ӧ'''
        pass

    def OnRspTradingAccountPasswordUpdate(self, pTradingAccountPasswordUpdate, pRspInfo, nRequestID, bIsLast):
        '''�ʽ��˻��������������Ӧ'''
        pass

    def OnRtnRepealFromFutureToBankByFutureManual(self, pRspRepeal):
        '''ϵͳ����ʱ�ڻ����ֹ���������ڻ�ת�����������д�����Ϻ��̷��ص�֪ͨ'''
        pass

    def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
        '''Ͷ���߽�����ȷ����Ӧ'''
        pass

    def OnRtnRepealFromBankToFutureByFutureManual(self, pRspRepeal):
        '''ϵͳ����ʱ�ڻ����ֹ������������ת�ڻ��������д�����Ϻ��̷��ص�֪ͨ'''
        pass

    def OnRtnFromFutureToBankByFuture(self, pRspTransfer):
        '''�ڻ������ڻ��ʽ�ת����֪ͨ'''
        pass

    def OnRspQryDepthMarketData(self, pDepthMarketData, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ������Ӧ'''
        pass

    def OnRspRemoveParkedOrderAction(self, pRemoveParkedOrderAction, pRspInfo, nRequestID, bIsLast):
        '''ɾ��Ԥ�񳷵���Ӧ'''
        pass

    def OnFrontConnected(self, ):
        '''���ͻ����뽻�׺�̨������ͨ������ʱ����δ��¼ǰ�����÷��������á�'''
        pass

    def OnRspQryInstrumentCommissionRate(self, pInstrumentCommissionRate, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ��Լ����������Ӧ'''
        pass

    def OnRtnRepealFromBankToFutureByBank(self, pRspRepeal):
        '''���з����������ת�ڻ�֪ͨ'''
        pass

    def OnRspQryOrder(self, pOrder, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ������Ӧ'''
        pass

    def OnRspQryTrade(self, pTrade, pRspInfo, nRequestID, bIsLast):
        '''�����ѯ�ɽ���Ӧ'''
        pass


class TraderApi:
    @staticmethod
    def CreateTraderApi(FlowPath="", IsUsingUdp=False):
        if FlowPath:
            FlowPath=os.path.abspath(FlowPath)
        api_ptr=_ctp_Trader.create_TraderApi(FlowPath, IsUsingUdp)
        return TraderApi(api_ptr)

    def __init__(self, api_ptr):
        self.api_ptr = api_ptr

    def ReqQryTradingAccount(self, pQryTradingAccount, nRequestID):
        '''�����ѯ�ʽ��˻�'''
        return _ctp_Trader.ReqQryTradingAccount(self.api_ptr, pQryTradingAccount, nRequestID)

    def ReqQryExchange(self, pQryExchange, nRequestID):
        '''�����ѯ������'''
        return _ctp_Trader.ReqQryExchange(self.api_ptr, pQryExchange, nRequestID)

    def ReqUserPasswordUpdate(self, pUserPasswordUpdate, nRequestID):
        '''�û������������'''
        return _ctp_Trader.ReqUserPasswordUpdate(self.api_ptr, pUserPasswordUpdate, nRequestID)

    def ReqQryTradingNotice(self, pQryTradingNotice, nRequestID):
        '''�����ѯ����֪ͨ'''
        return _ctp_Trader.ReqQryTradingNotice(self.api_ptr, pQryTradingNotice, nRequestID)

    def ReqQryTrade(self, pQryTrade, nRequestID):
        '''�����ѯ�ɽ�'''
        return _ctp_Trader.ReqQryTrade(self.api_ptr, pQryTrade, nRequestID)

    def ReqQueryMaxOrderVolume(self, pQueryMaxOrderVolume, nRequestID):
        '''��ѯ��󱨵���������'''
        return _ctp_Trader.ReqQueryMaxOrderVolume(self.api_ptr, pQueryMaxOrderVolume, nRequestID)

    def ReqSettlementInfoConfirm(self, pSettlementInfoConfirm, nRequestID):
        '''Ͷ���߽�����ȷ��'''
        return _ctp_Trader.ReqSettlementInfoConfirm(self.api_ptr, pSettlementInfoConfirm, nRequestID)

    def ReqQryInvestorPosition(self, pQryInvestorPosition, nRequestID):
        '''�����ѯͶ���ֲ߳�'''
        return _ctp_Trader.ReqQryInvestorPosition(self.api_ptr, pQryInvestorPosition, nRequestID)

    def ReqQryBrokerTradingAlgos(self, pQryBrokerTradingAlgos, nRequestID):
        '''�����ѯ���͹�˾�����㷨'''
        return _ctp_Trader.ReqQryBrokerTradingAlgos(self.api_ptr, pQryBrokerTradingAlgos, nRequestID)

    def ReqQryOrder(self, pQryOrder, nRequestID):
        '''�����ѯ����'''
        return _ctp_Trader.ReqQryOrder(self.api_ptr, pQryOrder, nRequestID)

    def Init(self, ):
        '''��ʼ��
@remark ��ʼ�����л���,ֻ�е��ú�,�ӿڲſ�ʼ����'''
        return _ctp_Trader.Init(self.api_ptr, )

    def ReqQryTradingCode(self, pQryTradingCode, nRequestID):
        '''�����ѯ���ױ���'''
        return _ctp_Trader.ReqQryTradingCode(self.api_ptr, pQryTradingCode, nRequestID)

    def ReqUserLogin(self, pReqUserLoginField, nRequestID):
        '''�û���¼����'''
        return _ctp_Trader.ReqUserLogin(self.api_ptr, pReqUserLoginField, nRequestID)

    def ReqFromFutureToBankByFuture(self, pReqTransfer, nRequestID):
        '''�ڻ������ڻ��ʽ�ת��������'''
        return _ctp_Trader.ReqFromFutureToBankByFuture(self.api_ptr, pReqTransfer, nRequestID)

    def RegisterSpi(self, pSpi):
        '''ע��ص��ӿ�
@param pSpi �����Իص��ӿ����ʵ��'''
        ret = _ctp_Trader.RegisterSpi(self.api_ptr, pSpi)
        pSpi.register_api(self)
        return ret

    def SubscribePublicTopic(self, nResumeType):
        '''���Ĺ�������
@param nResumeType �������ش���ʽ
        THOST_TERT_RESTART:�ӱ������տ�ʼ�ش�
        THOST_TERT_RESUME:���ϴ��յ�������
        THOST_TERT_QUICK:ֻ���͵�¼�󹫹���������
@remark �÷���Ҫ��Init����ǰ���á����������򲻻��յ������������ݡ�'''
        return _ctp_Trader.SubscribePublicTopic(self.api_ptr, nResumeType)

    def GetTradingDay(self, ):
        '''��ȡ��ǰ������
@retrun ��ȡ���Ľ�����
@remark ֻ�е�¼�ɹ���,���ܵõ���ȷ�Ľ�����'''
        return _ctp_Trader.GetTradingDay(self.api_ptr, )

    def ReqFromBankToFutureByFuture(self, pReqTransfer, nRequestID):
        '''�ڻ����������ʽ�ת�ڻ�����'''
        return _ctp_Trader.ReqFromBankToFutureByFuture(self.api_ptr, pReqTransfer, nRequestID)

    def ReqQryTransferSerial(self, pQryTransferSerial, nRequestID):
        '''�����ѯת����ˮ'''
        return _ctp_Trader.ReqQryTransferSerial(self.api_ptr, pQryTransferSerial, nRequestID)

    def ReqUserLogout(self, pUserLogout, nRequestID):
        '''�ǳ�����'''
        return _ctp_Trader.ReqUserLogout(self.api_ptr, pUserLogout, nRequestID)

    def ReqQryBrokerTradingParams(self, pQryBrokerTradingParams, nRequestID):
        '''�����ѯ���͹�˾���ײ���'''
        return _ctp_Trader.ReqQryBrokerTradingParams(self.api_ptr, pQryBrokerTradingParams, nRequestID)

    def ReqQrySettlementInfoConfirm(self, pQrySettlementInfoConfirm, nRequestID):
        '''�����ѯ������Ϣȷ��'''
        return _ctp_Trader.ReqQrySettlementInfoConfirm(self.api_ptr, pQrySettlementInfoConfirm, nRequestID)

    def ReqQryNotice(self, pQryNotice, nRequestID):
        '''�����ѯ�ͻ�֪ͨ'''
        return _ctp_Trader.ReqQryNotice(self.api_ptr, pQryNotice, nRequestID)

    def ReqParkedOrderInsert(self, pParkedOrder, nRequestID):
        '''Ԥ��¼������'''
        return _ctp_Trader.ReqParkedOrderInsert(self.api_ptr, pParkedOrder, nRequestID)

    def ReqQryContractBank(self, pQryContractBank, nRequestID):
        '''�����ѯǩԼ����'''
        return _ctp_Trader.ReqQryContractBank(self.api_ptr, pQryContractBank, nRequestID)

    def ReqQryInvestorPositionCombineDetail(self, pQryInvestorPositionCombineDetail, nRequestID):
        '''�����ѯͶ���ֲ߳���ϸ'''
        return _ctp_Trader.ReqQryInvestorPositionCombineDetail(self.api_ptr, pQryInvestorPositionCombineDetail, nRequestID)

    def ReqParkedOrderAction(self, pParkedOrderAction, nRequestID):
        '''Ԥ�񳷵�¼������'''
        return _ctp_Trader.ReqParkedOrderAction(self.api_ptr, pParkedOrderAction, nRequestID)

    def ReqQueryBankAccountMoneyByFuture(self, pReqQueryAccount, nRequestID):
        '''�ڻ������ѯ�����������'''
        return _ctp_Trader.ReqQueryBankAccountMoneyByFuture(self.api_ptr, pReqQueryAccount, nRequestID)

    def Join(self, ):
        '''�ȴ��ӿ��߳̽�������
@return �߳��˳�����'''
        return _ctp_Trader.Join(self.api_ptr, )

    def ReqQryParkedOrderAction(self, pQryParkedOrderAction, nRequestID):
        '''�����ѯԤ�񳷵�'''
        return _ctp_Trader.ReqQryParkedOrderAction(self.api_ptr, pQryParkedOrderAction, nRequestID)

    def ReqOrderInsert(self, pInputOrder, nRequestID):
        '''����¼������'''
        return _ctp_Trader.ReqOrderInsert(self.api_ptr, pInputOrder, nRequestID)

    def ReqQrySettlementInfo(self, pQrySettlementInfo, nRequestID):
        '''�����ѯͶ���߽�����'''
        return _ctp_Trader.ReqQrySettlementInfo(self.api_ptr, pQrySettlementInfo, nRequestID)

    def ReqQryInstrument(self, pQryInstrument, nRequestID):
        '''�����ѯ��Լ'''
        return _ctp_Trader.ReqQryInstrument(self.api_ptr, pQryInstrument, nRequestID)

    def ReqOrderAction(self, pInputOrderAction, nRequestID):
        '''������������'''
        return _ctp_Trader.ReqOrderAction(self.api_ptr, pInputOrderAction, nRequestID)

    def ReqQryInstrumentCommissionRate(self, pQryInstrumentCommissionRate, nRequestID):
        '''�����ѯ��Լ��������'''
        return _ctp_Trader.ReqQryInstrumentCommissionRate(self.api_ptr, pQryInstrumentCommissionRate, nRequestID)

    def Release(self, ):
        '''ɾ���ӿڶ�����
@remark ����ʹ�ñ��ӿڶ���ʱ,���øú���ɾ���ӿڶ���'''
        return _ctp_Trader.Release(self.api_ptr, )

    def ReqQryInstrumentMarginRate(self, pQryInstrumentMarginRate, nRequestID):
        '''�����ѯ��Լ��֤����'''
        return _ctp_Trader.ReqQryInstrumentMarginRate(self.api_ptr, pQryInstrumentMarginRate, nRequestID)

    def ReqQryInvestor(self, pQryInvestor, nRequestID):
        '''�����ѯͶ����'''
        return _ctp_Trader.ReqQryInvestor(self.api_ptr, pQryInvestor, nRequestID)

    def ReqQryDepthMarketData(self, pQryDepthMarketData, nRequestID):
        '''�����ѯ����'''
        return _ctp_Trader.ReqQryDepthMarketData(self.api_ptr, pQryDepthMarketData, nRequestID)

    def RegisterFront(self, pszFrontAddress):
        '''ע��ǰ�û������ַ
@param pszFrontAddress��ǰ�û������ַ��
@remark �����ַ�ĸ�ʽΪ����protocol://ipaddress:port�����磺��tcp://127.0.0.1:17001����
@remark ��tcp��������Э�飬��127.0.0.1�������������ַ����17001������������˿ںš�'''
        return _ctp_Trader.RegisterFront(self.api_ptr, pszFrontAddress)

    def ReqRemoveParkedOrderAction(self, pRemoveParkedOrderAction, nRequestID):
        '''����ɾ��Ԥ�񳷵�'''
        return _ctp_Trader.ReqRemoveParkedOrderAction(self.api_ptr, pRemoveParkedOrderAction, nRequestID)

    def ReqQryTransferBank(self, pQryTransferBank, nRequestID):
        '''�����ѯת������'''
        return _ctp_Trader.ReqQryTransferBank(self.api_ptr, pQryTransferBank, nRequestID)

    def ReqQryCFMMCTradingAccountKey(self, pQryCFMMCTradingAccountKey, nRequestID):
        '''�����ѯ��֤����ϵͳ���͹�˾�ʽ��˻���Կ'''
        return _ctp_Trader.ReqQryCFMMCTradingAccountKey(self.api_ptr, pQryCFMMCTradingAccountKey, nRequestID)

    def ReqTradingAccountPasswordUpdate(self, pTradingAccountPasswordUpdate, nRequestID):
        '''�ʽ��˻������������'''
        return _ctp_Trader.ReqTradingAccountPasswordUpdate(self.api_ptr, pTradingAccountPasswordUpdate, nRequestID)

    def ReqQryAccountregister(self, pQryAccountregister, nRequestID):
        '''�����ѯ����ǩԼ��ϵ'''
        return _ctp_Trader.ReqQryAccountregister(self.api_ptr, pQryAccountregister, nRequestID)

    def ReqQryParkedOrder(self, pQryParkedOrder, nRequestID):
        '''�����ѯԤ��'''
        return _ctp_Trader.ReqQryParkedOrder(self.api_ptr, pQryParkedOrder, nRequestID)

    def ReqQryEWarrantOffset(self, pQryEWarrantOffset, nRequestID):
        '''�����ѯ�ֵ��۵���Ϣ'''
        return _ctp_Trader.ReqQryEWarrantOffset(self.api_ptr, pQryEWarrantOffset, nRequestID)

    def ReqQryInvestorPositionDetail(self, pQryInvestorPositionDetail, nRequestID):
        '''�����ѯͶ���ֲ߳���ϸ'''
        return _ctp_Trader.ReqQryInvestorPositionDetail(self.api_ptr, pQryInvestorPositionDetail, nRequestID)

    def ReqRemoveParkedOrder(self, pRemoveParkedOrder, nRequestID):
        '''����ɾ��Ԥ��'''
        return _ctp_Trader.ReqRemoveParkedOrder(self.api_ptr, pRemoveParkedOrder, nRequestID)

    def SubscribePrivateTopic(self, nResumeType):
        '''����˽������
@param nResumeType ˽�����ش���ʽ
        THOST_TERT_RESTART:�ӱ������տ�ʼ�ش�
        THOST_TERT_RESUME:���ϴ��յ�������
        THOST_TERT_QUICK:ֻ���͵�¼��˽����������
@remark �÷���Ҫ��Init����ǰ���á����������򲻻��յ�˽���������ݡ�'''
        return _ctp_Trader.SubscribePrivateTopic(self.api_ptr, nResumeType)

