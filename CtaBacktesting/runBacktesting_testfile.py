from __future__ import division
from functools import reduce
import pandas as pd
from ctaStrategy.ctaBacktesting import BacktestingEngine
from ctaStrategy.strategy.strategyStockDayTrade import StockDayTradeStrategy

def runBackTesting(symbol):
    engine = BacktestingEngine()
    # 设置引擎的回测模式为K线
    engine.setBacktestingMode(engine.TICK_MODE)
    # 设置回测用的数据起始日期
    engine.setStartDate('20190408')
    engine.setEndDate('20190520')
    # 设置产品相关参数
    engine.setSlippage(0.00)
    engine.setRate(7 / 10000)
    engine.setSize(100)
    engine.setPriceTick(0.01)

    # 设置使用的历史数据库
    engine.setDatabase('stock_tick_data', ['IF888', symbol])

    # 在引擎中创建策略对象
    d = {}
    engine.initStrategy(StockDayTradeStrategy, d)
    # 开始跑回测
    engine.runBacktesting()
    # 显示回测结果
    engine.showBacktestingResult()
    df = engine.calculateBacktestingResult()
    return df


if __name__ == '__main__':

    df1 = runBackTesting('601888.SH')
    print("---------------------------------")
    df2 = runBackTesting('000063.SZ')
    print("---------------------------------")
    df3 = runBackTesting('601318.SH')
    print("---------------------------------")
    df4 = runBackTesting('600050.SH')
    print("---------------------------------")
    df5 = runBackTesting('600570.SH')
    print("---------------------------------")
    df6 = runBackTesting('002415.SZ')
    print("---------------------------------")
    df7 = runBackTesting('600585.SH')
    print("---------------------------------")
    df8 = runBackTesting('601336.SH')
    print("---------------------------------")
    df9 = runBackTesting('600030.SH')
    print("---------------------------------")
    df10 = runBackTesting('600309.SH')






