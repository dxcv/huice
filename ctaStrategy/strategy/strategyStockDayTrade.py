from ctaStrategy.ctaTemplate import CtaTemplate
from vtUtility import BarGenerator, ArrayManager2


class StockDayTradeStrategy(CtaTemplate):
    className = 'StockDayTradeStrategy'
    author = u'zjj_Tmac'

    # 策略参数
    fixed_stop_rate = 0.0014
    fixed_win_rate = 0.0014 * 3
    spread_rate = 1
    tick_nums = 5

    # 策略变量
    last_price = 0
    minus = 0
    fixed_long_stop = 0
    fixed_long_win = 0
    fixed_short_stop = 0
    fixed_short_win = 0
    order_qty = 0
    long_moving_win_list = []
    short_moving_win_list = []
    tick_after_open = 0
    pk_ask = {}
    pk_bid = {}

    # 参数列表，保存了参数的名称
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',
                 'spread_rate',
                 'tick_nums'
                 ]

    # 变量列表，保存了变量的名称
    varList = ['inited',
               'trading',
               'pos']

    # 同步列表，保存了需要保存到数据库的变量名称
    syncList = ['pos']

    # ----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        """Constructor"""
        super(StockDayTradeStrategy, self).__init__(ctaEngine, setting)

        # 创建K线合成器对象
        self.bg = BarGenerator(self.onBar)
        # 创建K线管理器
        self.am = ArrayManager2()

        # 注意策略类中的可变对象属性（通常是list和dict等），在策略初始化时需要重新创建，
        # 否则会出现多个策略实例之间数据共享的情况，有可能导致潜在的策略逻辑错误风险，
        # 策略类中的这些可变对象属性可以选择不写，全都放在__init__下面，写主要是为了阅读
        # 策略时方便（更多是个编程习惯的选择）

    # ----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略初始化' % self.name)
        for symbol in self.vtSymbol:
            self.am[symbol] = ArrayManager2()
        # 载入历史数据，并采用回放计算的方式初始化策略数值
        initData = self.loadBar(days=0)   # 等价于loadinitdata参数没有意义
        for data in initData:
            if data.vtSymbol == 'IF888':
                self.onBar(data)
            else:
                self.onTick(data)

        self.putEvent()

    # ----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略启动' %self.name)
        self.putEvent()

    # ----------------------------------------------------------------------
    def onStop(self):
        """停止策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略停止' %self.name)
        self.putEvent()

    # ----------------------------------------------------------------------
    def onTick(self, tick):
        """收到行情TICK推送（必须由用户继承实现）"""
        self.cancelAll()

        self.last_price = tick.lastPrice
        minus = self.minus
        iftradetime = int(tick.time) > 93200 and int(tick.time) < 145700
        bid_volumn = (tick.bidVolume1, tick.bidVolume2, tick.bidVolume3, tick.bidVolume4, tick.bidVolume5)
        bid_price = (tick.bidPrice1, tick.bidPrice2, tick.bidPrice3, tick.bidPrice4, tick.bidPrice5)
        self.pk_bid = dict(zip(bid_price, bid_volumn))
        ask_volumn = (tick.askVolume1, tick.askVolume2, tick.askVolume3, tick.askVolume4, tick.askVolume5)
        ask_price = (tick.askPrice1, tick.askPrice2, tick.askPrice3, tick.askPrice4, tick.askPrice5)
        self.pk_ask = dict(zip(ask_price, ask_volumn))

        # 持有多仓
        if self.pos > 0:
            # 检测价差
            spread = tick.askPrice2 - tick.bidPrice2

            # 跟踪止盈
            self.tick_after_open = self.tick_after_open + 1
            moving_win = max(self.pk_bid, key=self.pk_bid.get)
            win_max = max(self.long_moving_win_list)
            if moving_win > win_max:
                self.long_moving_win_list.append(moving_win)

            # 当最大盈利值超过固定盈利值，且价格不再创新高后 卖出
            if win_max > self.fixed_long_win:
                if tick.lastPrice < self.long_moving_win_list[-1]:
                    stop_price = tick.bidPrice1 - 1.0
                    self.sell(stop_price, abs(self.pos), stop=True)

            # 固定止损
            if tick.bidPrice1 <= self.fixed_long_stop:
                if self.tick_after_open >= self.tick_nums:
                    self.sell(tick.bidPrice1 - 1.0, abs(self.pos), stop=True)

            # 临近午盘若有仓位清仓
            if int(tick.time) > 112945 and int(tick.time) < 112956:
                self.sell(tick.bidPrice1 - 1.0, abs(self.pos), stop=True)

        # 持有空仓
        if self.pos < 0:
            # 检测价差
            spread = tick.askPrice2 - tick.bidPrice2

            # 跟踪止盈
            self.tick_after_open = self.tick_after_open + 1
            moving_win = max(self.pk_ask, key=self.pk_ask.get)
            win_min = min(self.short_moving_win_list)

            if moving_win < win_min:
                self.short_moving_win_list.append(moving_win)
            if win_min < self.fixed_short_win:
                if tick.lastPrice > self.short_moving_win_list[-1]:
                    stop_price = tick.askPrice1 + 1.0
                    self.cover(stop_price, abs(self.pos), stop=True)

            # 固定止损
            if tick.askPrice1 > self.fixed_short_stop:
                if self.tick_after_open >= self.tick_nums:
                    self.cover(tick.askPrice2, abs(self.pos), stop=True)

            # 临近午盘若有仓位清仓
            if int(tick.time) > 112945 and int(tick.time) < 112956:
                self.cover(tick.askPrice2, abs(self.pos), stop=True)

        # 股指大涨
        if minus > 6 and iftradetime:
            if self.pos == 0 and self.trading:
                self.order_qty = round(1000 / tick.lastPrice)
                self.buy(tick.askPrice1 + 1.0, self.order_qty)

        # 股指大跌
        elif minus < -6 and iftradetime:
            if self.pos == 0 and self.trading:
                self.order_qty = round(1000 / tick.lastPrice)
                self.short(tick.bidPrice1 - 1.0, self.order_qty)

            else:
                pass
        self.putEvent()

    # ----------------------------------------------------------------------
    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""
        self.minus = bar.close - bar.open
        self.putEvent()

    # ----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        pass

    # ----------------------------------------------------------------------
    def onTrade(self, trade):
        """收到成交推送（必须由用户继承实现）"""
        if trade.direction == '多' and trade.offset == '开仓':
            self.fixed_long_win = self.last_price + self.last_price * self.fixed_win_rate
            self.fixed_long_stop = self.last_price - self.last_price * self.fixed_stop_rate
            self.long_moving_win_list.append(self.fixed_long_win)
            self.minus = 0

        if trade.direction == '空' and trade.offset == '开仓':
            self.fixed_short_win = self.last_price - self.last_price * self.fixed_win_rate
            self.fixed_short_stop = self.last_price + self.last_price * self.fixed_stop_rate
            self.short_moving_win_list.append(self.fixed_short_win)
            self.minus = 0

        if trade.direction == '空' and trade.offset == '平仓':
            self.long_moving_win_list.clear()
            self.tick_after_open = 0

        if trade.direction == '多' and trade.offset == '平仓':
            self.short_moving_win_list.clear()
            self.tick_after_open = 0

    # ----------------------------------------------------------------------
    def onStopOrder(self, so):
        pass
        """停止单推送"""


