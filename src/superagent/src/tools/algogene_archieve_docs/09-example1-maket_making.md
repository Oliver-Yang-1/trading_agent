```python
from AlgoAPI import AlgoAPIUtil, AlgoAPI_Backtest
from datetime import datetime, timedelta

class AlgoEvent:
    """
    做市商策略类，通过在买卖价差间持续挂单来赚取价差收益
    """
    def __init__(self):
        """
        初始化策略参数
        lasttradetime: 上次交易时间，用于控制交易频率
        """
        self.lasttradetime = datetime(2000,1,1)

    def start(self, mEvt):
        """
        策略启动函数，初始化事件处理器
        
        参数:
            mEvt: 包含订阅列表等策略配置信息的字典
        """
        self.evt = AlgoAPI_Backtest.AlgoEvtHandler(self, mEvt)
        self.evt.start()

    def on_bulkdatafeed(self, isSync, bd, ab):
        """
        批量数据馈送回调函数
        
        参数:
            isSync: 是否为同步数据
            bd: 批量市场数据字典
            ab: 账户余额信息
        """
        pass

    def on_marketdatafeed(self, md, ab):
        """
        市场数据馈送回调函数，每24小时执行一次做市商策略
        
        参数:
            md: 市场数据对象，包含timestamp、bidPrice和askPrice等信息
            ab: 账户余额信息
        """
        if md.timestamp >= self.lasttradetime + timedelta(hours=24):
            self.test_sendOrder(md, 1, 'open')    # 发送买入限价单
            self.test_sendOrder(md, -1, 'open')   # 发送卖出限价单
            self.lasttradetime = md.timestamp

    def on_orderfeed(self, of):
        """
        订单馈送回调函数
        
        参数:
            of: 订单反馈信息
        """
        pass

    def on_dailyPLfeed(self, pl):
        """
        每日盈亏馈送回调函数
        
        参数:
            pl: 每日盈亏信息
        """
        pass

    def on_openPositionfeed(self, op, oo, uo):
        """
        持仓信息馈送回调函数
        
        参数:
            op: 开仓位置信息
            oo: 未完成订单信息
            uo: 更新的订单信息
        """
        pass

    def test_sendOrder(self, md, buysell, openclose):
        """
        发送订单的辅助函数
        
        参数:
            md: 市场数据对象
            buysell: 1表示买入，-1表示卖出
            openclose: 开仓或平仓标识
        """
        order = AlgoAPIUtil.OrderObject(
            instrument = 'EURUSD',           # 交易品种：欧元美元
            orderRef = 1,                    # 订单参考号
            volume = 0.01,                   # 交易量
            openclose = openclose,           # 开仓/平仓标识
            buysell = buysell,              # 买入/卖出方向
            ordertype = 1,                   # 订单类型：1=限价单
            timeinforce = 60*60*24*7        # 订单有效期：一周（单位：秒）
        )
        if buysell==1:
            order.price = md.bidPrice - 0.00005  # 买入价格设为当前买价减去0.5个基点
        elif buysell==-1:
            order.price = md.askPrice + 0.00005  # 卖出价格设为当前卖价加上0.5个基点
        self.evt.sendOrder(order)

