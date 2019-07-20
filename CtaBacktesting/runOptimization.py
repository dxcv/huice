# encoding: UTF-8

"""
展示如何执行参数优化。
"""

from __future__ import division
from __future__ import print_function


from ctaStrategy.ctaBacktesting import BacktestingEngine, MINUTE_DB_NAME, OptimizationSetting


if __name__ == '__main__':
    from ctaStrategy.strategy.strategyStockDayTrade import StockDayTradeStrategy
    # 创建回测引擎
    engine = BacktestingEngine()
    
    # 设置引擎的回测模式为K线
    engine.setBacktestingMode(engine.TICK_MODE)

    # 设置回测用的数据起始日期
    engine.setStartDate('20190508')
    engine.setEndDate('20190520')

    # 设置产品相关参数
    engine.setSlippage(0.00)
    engine.setRate(7 / 10000)
    engine.setSize(100)
    engine.setPriceTick(0.01)
    
    # 设置使用的历史数据库
    engine.setDatabase('stock_tick_data', ['IF888', '002415.SZ'])
    
    # 跑优化
    setting = OptimizationSetting()                 # 新建一个优化任务设置对象
    setting.setOptimizeTarget('endBalance')            # 设置优化排序的目标是策略净盈利
    setting.addParameter('spread_rate', 0.5, 1, 0.1)
    setting.addParameter('fixed_stop_rate', 0.0010, 0.0020, 0.0001)
    setting.addParameter('fixed_win_rate', 0.0030, 0.0060, 0.0001)

    import time    
    start = time.time()
    
    # 运行单进程优化函数，自动输出结果，耗时：359秒
    #engine.runOptimization(AtrRsiStrategy, setting)            
    
    # 多进程优化，耗时：89秒
    result = engine.runParallelOptimization(StockDayTradeStrategy, setting)
    engine.outputOptimizeResult(result)
    
    print(u'耗时：%s' %(time.time()-start))