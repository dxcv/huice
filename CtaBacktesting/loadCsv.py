# encoding: UTF-8

"""
导入MC导出的CSV历史数据到MongoDB中
"""

from ctaStrategy.ctaBase import MINUTE_DB_NAME
from ctaStrategy.ctaHistoryData import loadMcCsv
from ctaStrategy.ctaHistoryData import loadTbCsv


if __name__ == '__main__':
    #loadMcCsv('IF0000_1min.csv', MINUTE_DB_NAME, 'IF0000')
    # loadMcCsv('rb0000_1min.csv', MINUTE_DB_NAME, 'rb0000')
    loadTbCsv('IF888_10s.csv', 'stock_tick_data', 'IF888')