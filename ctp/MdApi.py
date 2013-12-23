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

import _ctp_Md
import os
import UserApiStruct

_ctp_Md.register_struct(UserApiStruct)

class MdSpi:
    def register_api(self, api):
        self.api=api

    def OnFrontDisconnected(self, nReason):
        '''���ͻ����뽻�׺�̨ͨ�����ӶϿ�ʱ���÷��������á���������������API���Զ��������ӣ��ͻ��˿ɲ�������
@param nReason ����ԭ��
        0x1001 �����ʧ��
        0x1002 ����дʧ��
        0x2001 ����������ʱ
        0x2002 ��������ʧ��
        0x2003 �յ�������'''
        pass

    def OnRspUserLogout(self, pUserLogout, pRspInfo, nRequestID, bIsLast):
        '''�ǳ�������Ӧ'''
        pass

    def OnRtnDepthMarketData(self, pDepthMarketData):
        '''�������֪ͨ'''
        pass

    def OnRspSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        '''��������Ӧ��'''
        pass

    def OnRspUnSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        '''ȡ����������Ӧ��'''
        pass

    def OnHeartBeatWarning(self, nTimeLapse):
        '''������ʱ���档����ʱ��δ�յ�����ʱ���÷��������á�
@param nTimeLapse �����ϴν��ձ��ĵ�ʱ��'''
        pass

    def OnRspError(self, pRspInfo, nRequestID, bIsLast):
        '''����Ӧ��'''
        pass

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        '''��¼������Ӧ'''
        pass

    def OnFrontConnected(self, ):
        '''���ͻ����뽻�׺�̨������ͨ������ʱ����δ��¼ǰ�����÷��������á�'''
        pass


class MdApi:
    @staticmethod
    def CreateMdApi(FlowPath="", IsUsingUdp=False):
        if FlowPath:
            FlowPath=os.path.abspath(FlowPath)
        api_ptr=_ctp_Md.create_MdApi(FlowPath, IsUsingUdp)
        return MdApi(api_ptr)

    def __init__(self, api_ptr):
        self.api_ptr = api_ptr

    def ReqUserLogout(self, pUserLogout, nRequestID):
        '''�ǳ�����'''
        return _ctp_Md.ReqUserLogout(self.api_ptr, pUserLogout, nRequestID)

    def Join(self, ):
        '''�ȴ��ӿ��߳̽�������
@return �߳��˳�����'''
        return _ctp_Md.Join(self.api_ptr, )


    def UnSubscribeMarketData(self, InstrumentIDs):
        """����/�˶����顣
        @param ppInstrumentIDs list of ��ԼID
        """
        return _ctp_Md.UnSubscribeMarketData(self.api_ptr, InstrumentIDs)

    def RegisterFront(self, pszFrontAddress):
        '''ע��ǰ�û������ַ
@param pszFrontAddress��ǰ�û������ַ��
@remark �����ַ�ĸ�ʽΪ����protocol://ipaddress:port�����磺��tcp://127.0.0.1:17001����
@remark ��tcp��������Э�飬��127.0.0.1�������������ַ����17001������������˿ںš�'''
        return _ctp_Md.RegisterFront(self.api_ptr, pszFrontAddress)

    def Init(self, ):
        '''��ʼ��
@remark ��ʼ�����л���,ֻ�е��ú�,�ӿڲſ�ʼ����'''
        return _ctp_Md.Init(self.api_ptr, )

    def ReqUserLogin(self, pReqUserLoginField, nRequestID):
        '''�û���¼����'''
        return _ctp_Md.ReqUserLogin(self.api_ptr, pReqUserLoginField, nRequestID)

    def Release(self, ):
        '''ɾ���ӿڶ�����
@remark ����ʹ�ñ��ӿڶ���ʱ,���øú���ɾ���ӿڶ���'''
        return _ctp_Md.Release(self.api_ptr, )

    def GetTradingDay(self, ):
        '''��ȡ��ǰ������
@retrun ��ȡ���Ľ�����
@remark ֻ�е�¼�ɹ���,���ܵõ���ȷ�Ľ�����'''
        return _ctp_Md.GetTradingDay(self.api_ptr, )


    def SubscribeMarketData(self, InstrumentIDs):
        """����/�˶����顣
        @param ppInstrumentIDs list of ��ԼID
        """
        return _ctp_Md.SubscribeMarketData(self.api_ptr, InstrumentIDs)

    def RegisterSpi(self, pSpi):
        '''ע��ص��ӿ�
@param pSpi �����Իص��ӿ����ʵ��'''
        ret = _ctp_Md.RegisterSpi(self.api_ptr, pSpi)
        pSpi.register_api(self)
        return ret

