# encoding: UTF-8

"""
展示如何执行策略回测。
"""

from __future__ import division


from ctaStrategy.ctaBacktesting import BacktestingEngine
from ctaStrategy.strategy.strategyStockDayTrade import StockDayTradeStrategy


if __name__ == '__main__':
    
    # 创建回测引擎
    engine = BacktestingEngine()
    
    # 设置引擎的回测模式为K线
    engine.setBacktestingMode(engine.TICK_MODE)

    # 设置回测用的数据起始日期
    engine.setStartDate('20190508')
    engine.setEndDate('20190510')
    
    # 设置产品相关参数
    engine.setSlippage(0)
    engine.setRate(7/10000)
    engine.setSize(100)
    engine.setPriceTick(0.01)
    
    # 设置使用的历史数据库
    engine.setDatabase('stock_tick_data', ['IF888',  '601318.SH'])
    
    # 在引擎中创建策略对象
    d = {}
    engine.initStrategy(StockDayTradeStrategy, d)
    
    # 开始跑回测
    engine.runBacktesting()
    # 显示回测结果
    engine.showBacktestingResult()