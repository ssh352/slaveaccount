# coding:utf-8
import os
import arrow
from .ctp import TdApi
from .constant import *
from .object import *


class CtpTdApi(TdApi):
    """CTP交易API实现"""

    # ----------------------------------------------------------------------
    def __init__(self, gateway):
        """API对象的初始化函数"""
        super(CtpTdApi, self).__init__()

        self.gateway = gateway  # gateway对象

        self.reqID = 0  # 操作请求编号
        self.orderRef = 0  # 订单编号

        self.connectionStatus = False  # 连接状态
        self.loginStatus = False  # 登录状态
        self.authStatus = False  # 验证状态
        self.loginFailed = False  # 登录失败（账号密码错误）

        self.userID = u''  # 账号
        self.password = u''  # 密码
        self.brokerID = u''  # 经纪商代码
        self.address = u''  # 服务器地址

        self.frontID = 0  # 前置机编号
        self.sessionID = 0  # 会话编号

        self.posDict = {}
        self.symbolExchangeDict = {}  # 保存合约代码和交易所的印射关系
        self.symbolSizeDict = {}  # 保存合约代码和合约大小的印射关系

        self.requireAuthentication = False

    @property
    def gatewayName(self):
        return self.gateway.gatewayName

    @property
    def logger(self):
        return self.gateway.logger

    # ----------------------------------------------------------------------
    def onFrontConnected(self):
        """服务器连接"""
        self.connectionStatus = True

        self.logger.info(TRADING_SERVER_CONNECTED)

        if self.requireAuthentication:
            self.authenticate()
        else:
            self.login()

    # ----------------------------------------------------------------------
    def onFrontDisconnected(self, n):
        """服务器断开"""
        self.connectionStatus = False
        self.loginStatus = False
        self.gateway.tdConnected = False

        self.logger.info(TRADING_SERVER_DISCONNECTED)

    # ----------------------------------------------------------------------
    def onHeartBeatWarning(self, n):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspAuthenticate(self, data, error, n, last):
        """验证客户端回报"""
        if error['ErrorID'] == 0:
            self.authStatus = True

            self.logger.info(TRADING_SERVER_AUTHENTICATED)

            self.login()
        else:
            log = u'{}'.format(error['ErrorID'])
            log += error['ErrorMsg'].decode('gbk')
            self.logger.error(log)
            self.gateway.onError(error)

    # ----------------------------------------------------------------------
    def onRspUserLogin(self, data, error, n, last):
        """登陆回报"""
        # 如果登录成功，推送日志信息
        if error['ErrorID'] == 0:
            self.frontID = str(data['FrontID'])
            self.sessionID = str(data['SessionID'])
            self.loginStatus = True
            self.gateway.tdConnected = True

            self.logger.info(TRADING_SERVER_LOGIN)

            # 确认结算信息
            req = {}
            req['BrokerID'] = self.brokerID
            req['InvestorID'] = self.userID
            self.reqID += 1
            self.reqSettlementInfoConfirm(req, self.reqID)

            # 否则，推送错误信息
        else:
            log = u'{}'.format(error['ErrorID'])
            log += error['ErrorMsg'].decode('gbk')
            self.logger.error(log)
            self.gateway.onError(error)

            # 标识登录失败，防止用错误信息连续重复登录
            self.loginFailed = True

    # ----------------------------------------------------------------------
    def onRspUserLogout(self, data, error, n, last):
        """登出回报"""
        # 如果登出成功，推送日志信息
        if error['ErrorID'] == 0:
            self.loginStatus = False
            self.gateway.tdConnected = False

            self.logger.info(TRADING_SERVER_LOGOUT)

        # 否则，推送错误信息
        else:
            log = u'{}'.format(error['ErrorID'])
            log += error['ErrorMsg'].decode('gbk')
            self.logger.error(log)
            self.gateway.onError(error)

    # ----------------------------------------------------------------------
    def onRspUserPasswordUpdate(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspTradingAccountPasswordUpdate(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspOrderInsert(self, data, error, n, last):
        """发单错误（柜台）"""
        # # 推送委托信息
        # order = VtOrderData()
        # order.gatewayName = self.gatewayName
        # order.symbol = data['InstrumentID']
        # order.exchange = exchangeMapReverse[data['ExchangeID']]
        # order.vtSymbol = order.symbol
        # order.orderID = data['OrderRef']
        # order.vtOrderID = '.'.join([self.gatewayName, order.orderID])
        # order.direction = directionMapReverse.get(data['Direction'], DIRECTION_UNKNOWN)
        # order.offset = offsetMapReverse.get(data['CombOffsetFlag'], OFFSET_UNKNOWN)
        # order.status = STATUS_REJECTED
        # order.price = data['LimitPrice']
        # order.totalVolume = data['VolumeTotalOriginal']
        # self.gateway.onOrder(order)
        #
        # # 推送错误信息
        # err = VtErrorData()
        # err.gatewayName = self.gatewayName
        # err.errorID = error['ErrorID']
        # err.errorMsg = error['ErrorMsg'].decode('gbk')
        # self.gateway.onError(err)

    # ----------------------------------------------------------------------
    def onRspParkedOrderInsert(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspParkedOrderAction(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspOrderAction(self, data, error, n, last):
        """撤单错误（柜台）"""
        # err = VtErrorData()
        # err.gatewayName = self.gatewayName
        # err.errorID = error['ErrorID']
        # err.errorMsg = error['ErrorMsg'].decode('gbk')
        # self.gateway.onError(err)

    # ----------------------------------------------------------------------
    def onRspQueryMaxOrderVolume(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspSettlementInfoConfirm(self, data, error, n, last):
        """确认结算信息回报"""
        self.logger.info(SETTLEMENT_INFO_CONFIRMED)

        # 查询合约代码
        self.reqID += 1
        self.reqQryInstrument({}, self.reqID)

    # ----------------------------------------------------------------------
    def onRspRemoveParkedOrder(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspRemoveParkedOrderAction(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspExecOrderInsert(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspExecOrderAction(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspForQuoteInsert(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQuoteInsert(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQuoteAction(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspLockInsert(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspCombActionInsert(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryOrder(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryTrade(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryInvestorPosition(self, data, error, n, last):
        """持仓查询回报"""
        if not data['InstrumentID']:
            return

        # 获取持仓缓存对象
        posName = '.'.join([data['InstrumentID'], data['PosiDirection']])
        if posName in self.posDict:
            pos = self.posDict[posName]
        else:
            pos = VtPositionData()
            self.posDict[posName] = pos

            pos.gatewayName = self.gatewayName
            pos.symbol = data['InstrumentID']
            pos.vtSymbol = pos.symbol
            pos.direction = posiDirectionMapReverse.get(data['PosiDirection'], '')
            pos.vtPositionName = '.'.join([pos.vtSymbol, pos.direction])

            # 针对上期所持仓的今昨分条返回（有昨仓、无今仓），读取昨仓数据
        if data['YdPosition'] and not data['TodayPosition']:
            pos.ydPosition = data['Position']

        # 计算成本
        size = self.symbolSizeDict[pos.symbol]
        cost = pos.price * pos.position * size

        # 汇总总仓
        pos.position += data['Position']
        pos.positionProfit += data['PositionProfit']

        # 计算持仓均价
        if pos.position and size:
            pos.price = (cost + data['PositionCost']) / (pos.position * size)

        # 读取冻结
        if pos.direction is DIRECTION_LONG:
            pos.frozen += data['LongFrozen']
        else:
            pos.frozen += data['ShortFrozen']

        # 查询回报结束
        if last:
            # 遍历推送
            for pos in self.posDict.values():
                self.gateway.onPosition(pos)

            # 清空缓存
            self.posDict.clear()

    # ----------------------------------------------------------------------
    def onRspQryTradingAccount(self, data, error, n, last):
        """资金账户查询回报"""
        account = VtAccountData()

        # 账户代码
        account.accountID = data['AccountID']

        # 数值相关
        account.preBalance = data['PreBalance']
        account.available = data['Available']
        account.commission = data['Commission']
        account.margin = data['CurrMargin']
        account.closeProfit = data['CloseProfit']
        account.positionProfit = data['PositionProfit']

        # 这里的balance和快期中的账户不确定是否一样，需要测试
        account.balance = (data['PreBalance'] - data['PreCredit'] - data['PreMortgage'] +
                           data['Mortgage'] - data['Withdraw'] + data['Deposit'] +
                           data['CloseProfit'] + data['PositionProfit'] + data['CashIn'] -
                           data['Commission'])

        # 推送
        self.gateway.onAccount(account)

    # ----------------------------------------------------------------------
    def onRspQryInvestor(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryTradingCode(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryInstrumentMarginRate(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryInstrumentCommissionRate(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryExchange(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryProduct(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryInstrument(self, data, error, n, last):
        """合约查询回报"""
        contract = VtContractData()
        contract.gatewayName = self.gatewayName

        contract.symbol = data['InstrumentID']
        contract.exchange = exchangeMapReverse[data['ExchangeID']]
        contract.vtSymbol = contract.symbol  # '.'.join([contract.symbol, contract.exchange])
        contract.name = data['InstrumentName'].decode('GBK')

        # 合约数值
        contract.size = data['VolumeMultiple']
        contract.priceTick = data['PriceTick']
        contract.strikePrice = data['StrikePrice']
        contract.productClass = productClassMapReverse.get(data['ProductClass'], PRODUCT_UNKNOWN)
        contract.expiryDate = data['ExpireDate']

        # ETF期权的标的命名方式需要调整（ETF代码 + 到期月份）
        if contract.exchange in [EXCHANGE_SSE, EXCHANGE_SZSE]:
            contract.underlyingSymbol = '-'.join([data['UnderlyingInstrID'], str(data['ExpireDate'])[2:-2]])
        # 商品期权无需调整
        else:
            contract.underlyingSymbol = data['UnderlyingInstrID']

            # 期权类型
        if contract.productClass is PRODUCT_OPTION:
            if data['OptionsType'] == '1':
                contract.optionType = OPTION_CALL
            elif data['OptionsType'] == '2':
                contract.optionType = OPTION_PUT

        # 缓存代码和交易所的印射关系
        self.symbolExchangeDict[contract.symbol] = contract.exchange
        self.symbolSizeDict[contract.symbol] = contract.size

        # 推送
        self.gateway.onContract(contract)

        # 缓存合约代码和交易所映射
        symbolExchangeDict[contract.symbol] = contract.exchange

        if last:
            self.logger.info(TRADING_SERVER_DISCONNECTED)

    # ----------------------------------------------------------------------
    def onRspQryDepthMarketData(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQrySettlementInfo(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryTransferBank(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryInvestorPositionDetail(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryNotice(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQrySettlementInfoConfirm(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryInvestorPositionCombineDetail(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryCFMMCTradingAccountKey(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryEWarrantOffset(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryInvestorProductGroupMargin(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryExchangeMarginRate(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryExchangeMarginRateAdjust(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryExchangeRate(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQrySecAgentACIDMap(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryProductExchRate(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryProductGroup(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryOptionInstrTradeCost(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryOptionInstrCommRate(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryExecOrder(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryForQuote(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryQuote(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryLock(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryLockPosition(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryInvestorLevel(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryExecFreeze(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryCombInstrumentGuard(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryCombAction(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryTransferSerial(self, data, error, n, last):
        """响应查询转账记录"""
        if not data['InvestorID']:
            # j
            return
        _data = {}
        for k, v in data.items():
            try:
                u'{} {}'.format(k, v)
            except UnicodeDecodeError:
                v = v.decode('gbk')
            _data[k] = v
        data = _data

        transferSerial = VtTransferSerialData()
        transferSerial.gatewayName = self.gatewayName
        print(data)
        # 转化日期
        tradingDay = data['TradingDay']
        print(tradingDay)
        tradingDay = '{}-{}-{} 00:00:00+08'.format(tradingDay[:4], tradingDay[4:6], tradingDay[6:8])
        print(tradingDay)
        transferSerial.tradingDay = arrow.get(tradingDay).datetime

        tradeDate = data['TradeDate']
        tradeTime = data['TradeTime']
        tradeDate = '{}-{}-{}'.format(tradeDate[:4], tradeDate[4:6], tradeDate[6:8])
        tradeTime = '{}+08'.format(tradeTime)
        tradeDatetime = '{} {}'.format(tradeDate, tradeTime)
        transferSerial.tradeDatetime = arrow.get(tradeDatetime).datetime

        # 转账金额
        transferSerial.tradeAmount = data['TradeAmount']
        # 转账类型
        transferSerial.tradeCode = data['TradeCode']

        # 当日的流水号，唯一标志
        transferSerial.futureSerial = data['FutureSerial']

        transferSerial.bankNewAccount = data['BankNewAccount']
        transferSerial.brokerBranchID = data['BrokerBranchID']
        transferSerial.operatorCode = data['OperatorCode']
        transferSerial.accountID = data['AccountID']
        transferSerial.bankAccount = data['BankAccount']
        transferSerial.bankBranchID = data['BankBranchID']
        transferSerial.sessionID = data['SessionID']
        transferSerial.bankID = data['BankID']
        transferSerial.plateSerial = data['PlateSerial']
        transferSerial.futureAccType = data['FutureAccType']
        transferSerial.errorID = data['ErrorID']
        transferSerial.bankSerial = data['BankSerial']
        transferSerial.identifiedCardNo = data['IdentifiedCardNo']
        transferSerial.brokerID = data['BrokerID']
        transferSerial.idCardType = data['IdCardType']
        transferSerial.custFee = data['CustFee']
        transferSerial.currencyID = data['CurrencyID']
        transferSerial.errorMsg = data['ErrorMsg']
        transferSerial.bankAccType = data['BankAccType']
        transferSerial.investorID = data['InvestorID']
        transferSerial.brokerFee = data['BrokerFee']
        transferSerial.availabilityFlag = data['AvailabilityFlag']

        self.gateway.onTransferSerial(transferSerial)

    # ----------------------------------------------------------------------
    def onRspQryAccountregister(self, data, error, n, last):
        """
        查询潜越银行的响应
        :param data:
        :param error:
        :param n:
        :param last:
        :return:
        """
        bankAccount = VtBankAccountData()
        bankAccount.bankAccount = data['BankAccount']
        bankAccount.customerName = data['CustomerName'].decode('gbk')
        bankAccount.currencyID = data['CurrencyID']
        bankAccount.brokerBranchID = data['BrokerBranchID']
        bankAccount.bankID = data['BankID']
        bankAccount.bankBranchID = data['BankBranchID']
        bankAccount.brokerID = data['BrokerID']
        bankAccount.accountID = data['AccountID']

        self.gateway.onAccountRegister(bankAccount)

    # ----------------------------------------------------------------------
    def onRspError(self, error, n, last):
        """错误回报"""
        log = u'{}'.format(error['ErrorID'])
        log += error['ErrorMsg'].decode('gbk')
        self.logger.error(log)
        self.gateway.onError(error)

    # ----------------------------------------------------------------------
    def onRtnOrder(self, data):
        """报单回报"""
        # 更新最大报单编号
        # newref = data['OrderRef']
        # self.orderRef = max(self.orderRef, int(newref))
        #
        # # 创建报单数据对象
        # order = VtOrderData()
        # order.gatewayName = self.gatewayName
        #
        # # 保存代码和报单号
        # order.symbol = data['InstrumentID']
        # order.exchange = exchangeMapReverse[data['ExchangeID']]
        # order.vtSymbol = order.symbol  # '.'.join([order.symbol, order.exchange])
        #
        # order.orderID = data['OrderRef']
        # # CTP的报单号一致性维护需要基于frontID, sessionID, orderID三个字段
        # # 但在本接口设计中，已经考虑了CTP的OrderRef的自增性，避免重复
        # # 唯一可能出现OrderRef重复的情况是多处登录并在非常接近的时间内（几乎同时发单）
        # # 考虑到VtTrader的应用场景，认为以上情况不会构成问题
        # order.vtOrderID = '.'.join([self.gatewayName, order.orderID])
        #
        # order.direction = directionMapReverse.get(data['Direction'], DIRECTION_UNKNOWN)
        # order.offset = offsetMapReverse.get(data['CombOffsetFlag'], OFFSET_UNKNOWN)
        # order.status = statusMapReverse.get(data['OrderStatus'], STATUS_UNKNOWN)
        #
        # # 价格、报单量等数值
        # order.price = data['LimitPrice']
        # order.totalVolume = data['VolumeTotalOriginal']
        # order.tradedVolume = data['VolumeTraded']
        # order.orderTime = data['InsertTime']
        # order.cancelTime = data['CancelTime']
        # order.frontID = data['FrontID']
        # order.sessionID = data['SessionID']
        #
        # # 推送
        # self.gateway.onOrder(order)

    # ----------------------------------------------------------------------
    def onRtnTrade(self, data):
        """成交回报"""
        # # 创建报单数据对象
        # trade = VtTradeData()
        # trade.gatewayName = self.gatewayName
        #
        # # 保存代码和报单号
        # trade.symbol = data['InstrumentID']
        # trade.exchange = exchangeMapReverse[data['ExchangeID']]
        # trade.vtSymbol = trade.symbol  # '.'.join([trade.symbol, trade.exchange])
        #
        # trade.tradeID = data['TradeID']
        # trade.vtTradeID = '.'.join([self.gatewayName, trade.tradeID])
        #
        # trade.orderID = data['OrderRef']
        # trade.vtOrderID = '.'.join([self.gatewayName, trade.orderID])
        #
        # # 方向
        # trade.direction = directionMapReverse.get(data['Direction'], '')
        #
        # # 开平
        # trade.offset = offsetMapReverse.get(data['OffsetFlag'], '')
        #
        # # 价格、报单量等数值
        # trade.price = data['Price']
        # trade.volume = data['Volume']
        # trade.tradeTime = data['TradeTime']
        #
        # # 推送
        # self.gateway.onTrade(trade)

    # ----------------------------------------------------------------------
    def onErrRtnOrderInsert(self, data, error):
        """发单错误回报（交易所）"""
        # 推送委托信息
        # order = VtOrderData()
        # order.gatewayName = self.gatewayName
        # order.symbol = data['InstrumentID']
        # order.exchange = exchangeMapReverse[data['ExchangeID']]
        # order.vtSymbol = order.symbol
        # order.orderID = data['OrderRef']
        # order.vtOrderID = '.'.join([self.gatewayName, order.orderID])
        # order.direction = directionMapReverse.get(data['Direction'], DIRECTION_UNKNOWN)
        # order.offset = offsetMapReverse.get(data['CombOffsetFlag'], OFFSET_UNKNOWN)
        # order.status = STATUS_REJECTED
        # order.price = data['LimitPrice']
        # order.totalVolume = data['VolumeTotalOriginal']
        # self.gateway.onOrder(order)
        #
        # # 推送错误信息
        # err = VtErrorData()
        # err.gatewayName = self.gatewayName
        # err.errorID = error['ErrorID']
        # err.errorMsg = error['ErrorMsg'].decode('gbk')
        # self.gateway.onError(err)

    # ----------------------------------------------------------------------
    def onErrRtnOrderAction(self, data, error):
        """撤单错误回报（交易所）"""
        log = u'{}'.format(error['ErrorID'])
        log += error['ErrorMsg'].decode('gbk')
        self.logger.error(log)
        self.gateway.onError(error)

    # ----------------------------------------------------------------------
    def onRtnInstrumentStatus(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnTradingNotice(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnErrorConditionalOrder(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnExecOrder(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onErrRtnExecOrderInsert(self, data, error):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onErrRtnExecOrderAction(self, data, error):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onErrRtnForQuoteInsert(self, data, error):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnQuote(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onErrRtnQuoteInsert(self, data, error):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onErrRtnQuoteAction(self, data, error):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnForQuoteRsp(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnCFMMCTradingAccountToken(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnLock(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onErrRtnLockInsert(self, data, error):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnCombAction(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onErrRtnCombActionInsert(self, data, error):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryContractBank(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryParkedOrder(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryParkedOrderAction(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryTradingNotice(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryBrokerTradingParams(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQryBrokerTradingAlgos(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQueryCFMMCTradingAccountToken(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnFromBankToFutureByBank(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnFromFutureToBankByBank(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnRepealFromBankToFutureByBank(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnRepealFromFutureToBankByBank(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnFromBankToFutureByFuture(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnFromFutureToBankByFuture(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnRepealFromBankToFutureByFutureManual(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnRepealFromFutureToBankByFutureManual(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnQueryBankBalanceByFuture(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onErrRtnBankToFutureByFuture(self, data, error):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onErrRtnFutureToBankByFuture(self, data, error):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onErrRtnRepealBankToFutureByFutureManual(self, data, error):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onErrRtnRepealFutureToBankByFutureManual(self, data, error):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onErrRtnQueryBankBalanceByFuture(self, data, error):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnRepealFromBankToFutureByFuture(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnRepealFromFutureToBankByFuture(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspFromBankToFutureByFuture(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspFromFutureToBankByFuture(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRspQueryBankAccountMoneyByFuture(self, data, error, n, last):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnOpenAccountByBank(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnCancelAccountByBank(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def onRtnChangeAccountByBank(self, data):
        """"""
        pass

    # ----------------------------------------------------------------------
    def connect(self, userID, password, brokerID, address, authCode, userProductInfo):
        """初始化连接"""
        self.userID = userID  # 账号
        self.password = password  # 密码
        self.brokerID = brokerID  # 经纪商代码
        self.address = address  # 服务器地址
        self.authCode = authCode  # 验证码
        self.userProductInfo = userProductInfo  # 产品信息

        # 如果尚未建立服务器连接，则进行连接
        if not self.connectionStatus:
            # 创建C++环境中的API对象，这里传入的参数是需要用来保存.con文件的文件夹路径
            path = self.gateway.config.get('CTP', 'connectionStatusPath')

            path = os.path.join(path, self.gateway.userID + '_')
            self.createFtdcTraderApi(path)

            # 设置数据同步模式为推送从今日开始所有数据
            self.subscribePrivateTopic(0)
            self.subscribePublicTopic(0)

            # 注册服务器地址
            self.registerFront(self.address)

            # 初始化连接，成功会调用onFrontConnected
            self.init()

        # 若已经连接但尚未登录，则进行登录
        else:
            if self.requireAuthentication and not self.authStatus:
                self.authenticate()
            elif not self.loginStatus:
                self.login()

    # ----------------------------------------------------------------------
    def login(self):
        """连接服务器"""
        # 如果之前有过登录失败，则不再进行尝试
        if self.loginFailed:
            return

        # 如果填入了用户名密码等，则登录
        if self.userID and self.password and self.brokerID:
            req = {}
            req['UserID'] = self.userID
            req['Password'] = self.password
            req['BrokerID'] = self.brokerID
            self.reqID += 1
            self.reqUserLogin(req, self.reqID)

            # ----------------------------------------------------------------------

    def authenticate(self):
        """申请验证"""
        if self.userID and self.brokerID and self.authCode and self.userProductInfo:
            req = {}
            req['UserID'] = self.userID
            req['BrokerID'] = self.brokerID
            req['AuthCode'] = self.authCode
            req['UserProductInfo'] = self.userProductInfo
            self.reqID += 1
            self.reqAuthenticate(req, self.reqID)

    # ----------------------------------------------------------------------
    def qryAccount(self):
        """查询账户"""
        self.reqID += 1
        self.reqQryTradingAccount({}, self.reqID)

    # ----------------------------------------------------------------------
    def qryPosition(self):
        """查询持仓"""
        self.reqID += 1
        req = {}
        req['BrokerID'] = self.brokerID
        req['InvestorID'] = self.userID
        self.reqQryInvestorPosition(req, self.reqID)

    def qryAccountregister(self):
        """
        查签约银行
        :return:
        """

        self.reqID += 1
        req = {
            'BrokerID': self.brokerID,
        }

        self.reqQryAccountregister(req, self.reqID)

    def qryTransferSerial(self):
        """查询入金"""
        self.reqID += 1
        amount = len(self.gateway.banks)
        count = 0
        for bank in self.gateway.banks.values():
            assert isinstance(bank, VtBankAccountData)

            req = {
                'CurrencyID': bank.currencyID,
                'BankID': bank.bankID,
                'BrokerID': bank.brokerID,
                'AccountID': bank.accountID,

            }
            self.reqQryTransferSerial(req, self.reqID)
            count += 1
            if count == amount:
                break
            time.sleep(3)

    # ----------------------------------------------------------------------
    def sendOrder(self, orderReq):
        """发单"""
        # self.reqID += 1
        # self.orderRef += 1
        #
        # req = {}
        #
        # req['InstrumentID'] = orderReq.symbol
        # req['LimitPrice'] = orderReq.price
        # req['VolumeTotalOriginal'] = orderReq.volume
        #
        # # 下面如果由于传入的类型本接口不支持，则会返回空字符串
        # req['OrderPriceType'] = priceTypeMap.get(orderReq.priceType, '')
        # req['Direction'] = directionMap.get(orderReq.direction, '')
        # req['CombOffsetFlag'] = offsetMap.get(orderReq.offset, '')
        #
        # req['OrderRef'] = str(self.orderRef)
        # req['InvestorID'] = self.userID
        # req['UserID'] = self.userID
        # req['BrokerID'] = self.brokerID
        #
        # req['CombHedgeFlag'] = defineDict['THOST_FTDC_HF_Speculation']  # 投机单
        # req['ContingentCondition'] = defineDict['THOST_FTDC_CC_Immediately']  # 立即发单
        # req['ForceCloseReason'] = defineDict['THOST_FTDC_FCC_NotForceClose']  # 非强平
        # req['IsAutoSuspend'] = 0  # 非自动挂起
        # req['TimeCondition'] = defineDict['THOST_FTDC_TC_GFD']  # 今日有效
        # req['VolumeCondition'] = defineDict['THOST_FTDC_VC_AV']  # 任意成交量
        # req['MinVolume'] = 1  # 最小成交量为1
        #
        # # 判断FAK和FOK
        # if orderReq.priceType == PRICETYPE_FAK:
        #     req['OrderPriceType'] = defineDict["THOST_FTDC_OPT_LimitPrice"]
        #     req['TimeCondition'] = defineDict['THOST_FTDC_TC_IOC']
        #     req['VolumeCondition'] = defineDict['THOST_FTDC_VC_AV']
        # if orderReq.priceType == PRICETYPE_FOK:
        #     req['OrderPriceType'] = defineDict["THOST_FTDC_OPT_LimitPrice"]
        #     req['TimeCondition'] = defineDict['THOST_FTDC_TC_IOC']
        #     req['VolumeCondition'] = defineDict['THOST_FTDC_VC_CV']
        #
        # self.reqOrderInsert(req, self.reqID)
        #
        # # 返回订单号（字符串），便于某些算法进行动态管理
        # vtOrderID = '.'.join([self.gatewayName, str(self.orderRef)])
        # return vtOrderID

    # ----------------------------------------------------------------------
    def cancelOrder(self, cancelOrderReq):
        """撤单"""
        # self.reqID += 1
        #
        # req = {}
        #
        # req['InstrumentID'] = cancelOrderReq.symbol
        # req['ExchangeID'] = cancelOrderReq.exchange
        # req['OrderRef'] = cancelOrderReq.orderID
        # req['FrontID'] = cancelOrderReq.frontID
        # req['SessionID'] = cancelOrderReq.sessionID
        #
        # req['ActionFlag'] = defineDict['THOST_FTDC_AF_Delete']
        # req['BrokerID'] = self.brokerID
        # req['InvestorID'] = self.userID
        #
        # self.reqOrderAction(req, self.reqID)

    # ----------------------------------------------------------------------
    def close(self):
        """关闭"""
        self.exit()
