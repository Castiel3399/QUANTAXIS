# coding :utf-8
#
# The MIT License (MIT)
#
# Copyright (c) 2016-2017 yutiansut/QUANTAXIS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import datetime

from QUANTAXIS.QAFetch.QAQuery import (QA_fetch_future_day,
                                       QA_fetch_future_min,
                                       QA_fetch_future_tick,
                                       QA_fetch_index_day, QA_fetch_index_min,
                                       QA_fetch_stock_day, QA_fetch_stock_min)
from QUANTAXIS.QAFetch.QATdx import (QA_fetch_get_future_day,
                                     QA_fetch_get_future_min,
                                     QA_fetch_get_future_transaction,
                                     QA_fetch_get_future_transaction_realtime,
                                     QA_fetch_get_index_day,
                                     QA_fetch_get_index_min,
                                     QA_fetch_get_stock_day,
                                     QA_fetch_get_stock_min)
from QUANTAXIS.QAMarket.QABroker import QA_Broker
from QUANTAXIS.QAMarket.QADealer import QA_Dealer
from QUANTAXIS.QAMarket.QATrade import QA_Trade
from QUANTAXIS.QAMarket.QAOrderHandler import QA_OrderHandler
from QUANTAXIS.QAMarket.QABacktestBroker import QA_BacktestBroker
from QUANTAXIS.QAMarket.QARandomBroker import QA_RandomBroker
from QUANTAXIS.QAMarket.QARealBroker import QA_RealBroker
from QUANTAXIS.QAMarket.QASimulatedBroker import QA_SimulatedBroker
from QUANTAXIS.QAARP.QAAccount import QA_Account
from QUANTAXIS.QAUtil.QALogs import QA_util_log_info
from QUANTAXIS.QAUtil.QAParameter import AMOUNT_MODEL, ORDER_MODEL, ORDER_EVENT, BROKER_TYPE


class QA_Market(QA_Trade):
    """
    QUANTAXIS MARKET 部分

    交易前置

    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.session = {}
        self.order_handler = QA_OrderHandler()
        self._broker = {BROKER_TYPE.BACKETEST: QA_BacktestBroker, BROKER_TYPE.RANODM: QA_RandomBroker,
                        BROKER_TYPE.REAL: QA_RealBroker, BROKER_TYPE.SIMULATION: QA_SimulatedBroker}
        self.broker_name = None
        self.broker = None

    def __repr__(self):
        return '< QA_MARKET with {} Broker >'.format(self.broker_name)

    def connect(self, broker):
        if broker in self._broker.keys():
            self.broker_name = broker
            self.broker = self._broker[broker]()
            return True
        else:
            return False

    def login(self, account_cookie):
        if account_cookie not in self.session.keys():
            self.session[account_cookie] = QA_Account(
                account_cookie=account_cookie)
        else:
            return False

    def logout(self, account_cookie):
        if account_cookie not in self.session.keys():
            return False
        else:
            self.session.pop(account_cookie)

    def get_trading_day(self):
        pass

    def get_account_id(self):
        return [item.account_cookie for item in self.session.values()]

    def insert_order(self, account_id, amount, amount_model, time, code, order_model, towards):

        order = self.session[account_id].send_order(
            amount=amount, amount_model=amount_model, time=time, code=code, order_model=order_model, towards=towards)
        self.on_insert_order(order.info())
        self.order_handler.order_event(event=ORDER_EVENT.CREATE, message=order)
        msg = self.order_handler.order_event(
            event=ORDER_EVENT.TRADE, message={'broker': self.broker})
        self.on_trade_event(msg)

    def on_insert_order(self,data):
        print(data)


if __name__ == '__main__':

    import QUANTAXIS as QA

    user = QA.QA_Portfolio()
    # 创建两个account

    a_1 = user.new_account()
    a_2 = user.new_account()
    market = QA_Market()

    market.connect(QA.RUNNING_ENVIRONMENT.BACKETEST)
    print(market)
    market.login(a_1)
    market.login(a_2)
    print(market.get_account_id())
    market.insert_order(account_id=a_1, amount=10000, amount_model=QA.AMOUNT_MODEL.BY_PRICE,
                        time='2017-12-14', code='000001', order_model=QA.ORDER_MODEL.CLOSE, towards=QA.ORDER_DIRECTION.BUY)