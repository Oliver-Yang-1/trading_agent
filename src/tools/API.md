# Trading Agent API 调用方法总结

本文档总结了 `src/tools` 文件夹中封装的所有 API 调用方法，为后续开发提供快速参考。

## 📁 目录结构

```
src/tools/
├── api.py                    # 核心金融数据 API
├── algogene_client.py        # Algogene 专业金融 API 客户端  
├── news_crawler.py           # 新闻爬虫和情感分析
├── stock_news_alt.py         # 备用股票新闻 API
├── openrouter_config.py      # LLM API 统一配置
├── data_analyzer.py          # 数据分析工具
├── code_interpreter.py       # Python 代码执行器
└── tests/                    # 测试文件
```

## 🔧 核心 API 模块

### 1. api.py - 核心金融数据 API

#### 1.1 财务指标获取

```python
def get_financial_metrics(symbol: str) -> Dict[str, Any]
```

**功能**: 获取股票财务指标数据，支持 A股、美股、加密货币

**参数**:
- `symbol`: 股票代码（如 "600519"、"AAPL"、"BTC"）

**返回数据结构**:
```python
{
    # 基础信息
    "market_cap": 500000000000,        # 总市值
    "shares_outstanding": 1250000000,   # 流通股本
    
    # 盈利能力指标
    "pe_ratio": 25.0,                  # 市盈率
    "price_to_book": 3.0,              # 市净率
    "price_to_sales": 2.5,             # 市销率
    "earnings_per_share": 8.5,         # 每股收益
    "return_on_equity": 0.15,          # 净资产收益率
    "net_margin": 0.12,                # 销售净利率
    "operating_margin": 0.18,          # 营业利润率
    
    # 增长指标
    "revenue_growth": 0.10,            # 营收增长率
    "earnings_growth": 0.15,           # 净利润增长率
    "book_value_growth": 0.08,         # 净资产增长率
    
    # 财务健康指标
    "current_ratio": 2.5,              # 流动比率
    "debt_to_equity": 0.3,             # 资产负债率
    "free_cash_flow_per_share": 5.2,   # 每股自由现金流
    
    # 基础财务数据
    "revenue": 50000000000,            # 总营收
    "net_income": 6000000000           # 净利润
}
```

**使用示例**:
```python
from src.tools.api import get_financial_metrics

# A股示例
metrics_a = get_financial_metrics("600519")  # 贵州茅台
print(f"PE比率: {metrics_a['pe_ratio']}")

# 美股示例  
metrics_us = get_financial_metrics("AAPL")   # 苹果
print(f"市值: {metrics_us['market_cap']}")

# 加密货币示例
metrics_crypto = get_financial_metrics("BTC") # 比特币
print(f"市值: {metrics_crypto['market_cap']}")
```

#### 1.2 财务报表获取

```python
def get_financial_statements(symbol: str) -> Dict[str, Any]
```

**功能**: 获取财务报表数据（利润表、资产负债表、现金流量表）

**返回数据**:
```python
[
    {  # 最新期间
        "net_income": 1000000000,              # 净利润
        "operating_revenue": 5000000000,       # 营业收入
        "operating_profit": 1200000000,        # 营业利润
        "working_capital": 800000000,          # 营运资金
        "depreciation_and_amortization": 50000000,  # 折旧摊销
        "capital_expenditure": 200000000,      # 资本支出
        "free_cash_flow": 600000000           # 自由现金流
    }
]
```

#### 1.3 市场数据获取

```python
def get_market_data(symbol: str) -> Dict[str, Any]
```

**功能**: 获取市场交易数据

**返回数据**:
```python
{
    "market_cap": 500000000000,        # 总市值
    "volume": 10000000,                # 成交量
    "average_volume": 12000000,        # 平均成交量
    "fifty_two_week_high": 120.0,      # 52周最高价
    "fifty_two_week_low": 80.0         # 52周最低价
}
```

#### 1.4 历史价格数据获取

```python
def get_price_history(symbol: str, start_date: str = None, end_date: str = None, 
                     adjust: str = "qfq") -> pd.DataFrame
```

**功能**: 获取股票历史价格数据，包含丰富的技术指标

**参数**:
- `symbol`: 股票代码
- `start_date`: 开始日期 "YYYY-MM-DD"，默认为一年前
- `end_date`: 结束日期 "YYYY-MM-DD"，默认为昨天
- `adjust`: 复权类型，"qfq"前复权/"hfq"后复权/""不复权

**返回的 DataFrame 列**:
```python
# 基础价格数据
'date', 'open', 'high', 'low', 'close', 'volume', 'amount',
'amplitude', 'pct_change', 'change_amount', 'turnover',

# 动量指标
'momentum_1m', 'momentum_3m', 'momentum_6m', 'volume_momentum',

# 波动率指标
'historical_volatility', 'volatility_regime', 'volatility_z_score', 'atr_ratio',

# 统计套利指标
'hurst_exponent', 'skewness', 'kurtosis'
```

**使用示例**:
```python
from src.tools.api import get_price_history

# 获取贵州茅台近一年数据
df = get_price_history("600519", "2023-01-01", "2023-12-31")
print(f"数据记录数: {len(df)}")
print(f"最新收盘价: {df['close'].iloc[-1]}")
```

---

### 2. algogene_client.py - Algogene 专业金融 API

#### 2.1 客户端初始化

```python
from src.tools.algogene_client import AlgogeneClient

client = AlgogeneClient(proxy="http://127.0.0.1:7890")  # 可选代理
```

**环境变量要求**:
- `ALGOGENE_API_KEY`: 您的 API 密钥
- `ALGOGENE_USER_ID`: 您的用户 ID
- `ALGOGENE_PROXY`: 代理 URL（可选）

#### 2.2 历史价格数据

```python
def get_price_history(count: int, instrument: str, interval: str, timestamp: str) -> Dict[str, Any]
```

**功能**: 获取专业级历史价格数据

**参数**:
- `count`: 数据点数量
- `instrument`: 交易工具符号（如 "GOOGL", "BTCUSD"）
- `interval`: 时间间隔（"M"月, "W"周, "D"日, "H"小时等）
- `timestamp`: 参考时间戳 "YYYY-MM-DD HH:MM:SS"

**返回数据**:
```python
{
    "res": [
        {
            "t": "2023-12-01 09:30:00",    # 时间戳（GMT+0）
            "o": 100.0,                    # 开盘价
            "h": 105.0,                    # 最高价
            "l": 99.0,                     # 最低价
            "c": 102.0,                    # 收盘价
            "b": 101.5,                    # 收盘买价
            "a": 102.5,                    # 收盘卖价
            "m": 102.0,                    # 收盘中位价
            "v": 1000,                     # 成交量
            "instrument": "GOOGL"          # 工具名称
        }
    ],
    "count": 1
}
```

#### 2.3 实时价格数据

```python
def get_realtime_price(symbols: str, broker: Optional[str] = None) -> Dict[str, Any]
```

**功能**: 获取实时市场价格

**参数**:
- `symbols`: 金融符号，多个用逗号分隔（如 "BTCUSD,ETHUSD"）
- `broker`: 特定经纪商（可选）: 'diginex', 'exness', 'ib', 'ig', 'oanda'

#### 2.4 其他专业数据接口

```python
# 经济日历
def get_econs_calendar(start_date: str = None, end_date: str = None, 
                      country: str = None) -> Dict[str, Any]

# 经济统计数据
def get_econs_statistics(series_id: str, start_date: str = None, 
                        end_date: str = None) -> Dict[str, Any]

# 历史新闻
def get_historical_news(count: int = 10, timestamp_lt: str = None,
                       timestamp_gt: str = None, language: str = "en",
                       category: str = None, source: str = None) -> Dict[str, Any]

# 实时汇率
def get_realtime_exchange_rate(cur1: str, cur2: str) -> Dict[str, Any]

# 实时经济统计
def get_realtime_econs_stat() -> Dict[str, Any]

# 实时天气
def get_realtime_weather(city: str) -> Dict[str, Any]

# 实时新闻
def get_realtime_news(count: int = 10, language: str = "en",
                     category: str = None, source: str = None) -> Dict[str, Any]
```

**使用示例**:
```python
from src.tools.algogene_client import AlgogeneClient

client = AlgogeneClient()

# 获取Google历史数据
history = client.get_price_history(
    count=5,
    instrument="GOOGL",
    interval="D",
    timestamp="2024-01-01 00:00:00"
)

# 获取比特币实时价格
realtime = client.get_realtime_price("BTCUSD")

# 获取美元兑欧元汇率
exchange_rate = client.get_realtime_exchange_rate("USD", "EUR")
```

---

### 3. news_crawler.py - 新闻爬虫和情感分析

#### 3.1 股票新闻获取

```python
def get_stock_news(symbol: str, market_type: str = "cn", max_news: int = 10) -> list
```

**功能**: 获取股票相关新闻，支持中美市场

**参数**:
- `symbol`: 股票代码
- `market_type`: 市场类型 "cn"中国/"us"美国，默认"cn"
- `max_news`: 获取新闻条数，默认10条，最大100条

**返回数据结构**:
```python
[
    {
        "title": "公司发布Q3财报，净利润同比增长15%",
        "content": "详细新闻内容...",
        "publish_time": "2023-12-01 10:30:00",
        "source": "财经日报",
        "url": "https://example.com/news/123",
        "keyword": "600519"
    }
]
```

#### 3.2 美股新闻获取

```python
def get_us_stock_news(symbol: str, max_news: int = 10) -> list
```

**功能**: 专门获取美股新闻

#### 3.3 中国股票新闻获取

```python
def get_cn_stock_news(symbol: str, max_news: int = 10) -> list
```

**功能**: 专门获取A股新闻

#### 3.4 新闻情感分析

```python
def get_news_sentiment(news_list: list, num_of_news: int = 5) -> float
```

**功能**: 使用 AI 分析新闻情感得分

**参数**:
- `news_list`: 新闻列表
- `num_of_news`: 分析的新闻数量，默认5条

**返回值**: 
- `float`: 情感得分，范围 [-1, 1]
  - **1**: 极其积极（重大利好消息）
  - **0.5-0.9**: 积极（业绩增长、获得大订单等）
  - **0**: 中性（日常公告、中性报道）
  - **-0.5--0.9**: 消极（业绩下滑、负面传言）
  - **-1**: 极其消极（重大违规、财务造假等）

**使用示例**:
```python
from src.tools.news_crawler import get_stock_news, get_news_sentiment

# 获取贵州茅台新闻
news = get_stock_news("600519", market_type="cn", max_news=15)
print(f"获取到 {len(news)} 条新闻")

# 分析新闻情感
sentiment = get_news_sentiment(news, num_of_news=10)
print(f"新闻情感得分: {sentiment}")

# 获取苹果公司美股新闻
us_news = get_stock_news("AAPL", market_type="us", max_news=10)
```

---

### 4. openrouter_config.py - LLM API 统一配置

#### 4.1 聊天完成接口

```python
def get_chat_completion(messages, model=None, max_retries=3, initial_retry_delay=1,
                        client_type="auto", api_key=None, base_url=None) -> str
```

**功能**: 获取 LLM 聊天完成结果，支持多种 AI 模型

**参数**:
- `messages`: 消息列表，OpenAI 格式
- `model`: 模型名称（可选）
- `max_retries`: 最大重试次数，默认3次
- `initial_retry_delay`: 初始重试延迟（秒），默认1秒
- `client_type`: 客户端类型
  - `"auto"`: 自动选择（默认）
  - `"gemini"`: Google Gemini
  - `"openai_compatible"`: OpenAI 兼容 API
- `api_key`: API 密钥（可选）
- `base_url`: API 基础 URL（可选）

**返回值**: 
- `str`: 模型回答内容，出错时返回 `None`

**支持的模型**:
- **Gemini**: `gemini-1.5-flash`, `gemini-1.5-pro`
- **OpenAI Compatible**: 支持 OpenRouter、DeepSeek 等

**使用示例**:
```python
from src.tools.openrouter_config import get_chat_completion

# 基本用法
messages = [
    {"role": "user", "content": "分析一下苹果公司的投资价值"}
]
response = get_chat_completion(messages)
print(response)

# 指定模型
response = get_chat_completion(
    messages, 
    model="gemini-1.5-pro",
    client_type="gemini"
)

# 使用 OpenAI 兼容 API
response = get_chat_completion(
    messages,
    client_type="openai_compatible",
    api_key="your-api-key",
    base_url="https://api.openrouter.ai/v1"
)
```

---

### 5. data_analyzer.py - 数据分析工具

#### 5.1 股票技术分析

```python
def analyze_stock_data(symbol: str, start_date: str = None, end_date: str = None)
```

**功能**: 获取股票历史数据并计算技术指标，保存为 CSV 文件

**参数**:
- `symbol`: 股票代码
- `start_date`: 开始日期 "YYYY-MM-DD"，默认一年前
- `end_date`: 结束日期 "YYYY-MM-DD"，默认昨天

**计算的技术指标**:

1. **移动平均线**:
   - `ma5`, `ma10`, `ma20`, `ma60`

2. **MACD**:
   - `macd`: MACD线
   - `signal_line`: 信号线
   - `macd_hist`: MACD柱状图

3. **RSI**:
   - `rsi`: 相对强弱指数（14期）

4. **布林带**:
   - `bb_upper`: 上轨
   - `bb_middle`: 中轨（20日MA）
   - `bb_lower`: 下轨

5. **成交量指标**:
   - `volume_ma5`: 5日成交量均线
   - `volume_ma20`: 20日成交量均线
   - `volume_ratio`: 成交量比率

6. **动量指标**:
   - `price_momentum`: 价格动量（5日）
   - `price_acceleration`: 价格加速度

7. **波动率指标**:
   - `daily_return`: 日收益率
   - `volatility_5d`: 5日波动率
   - `volatility_20d`: 20日波动率

**输出文件**: `{symbol}_analysis_{YYYYMMDD}.csv`

**使用示例**:
```python
from src.tools.data_analyzer import analyze_stock_data

# 分析贵州茅台过去一年的数据
analyze_stock_data("600519", "2023-01-01", "2023-12-31")

# 分析最近一年数据（默认）
analyze_stock_data("000001")  # 平安银行
```

---

### 6. code_interpreter.py - Python 代码执行器

#### 6.1 安全代码执行

```python
def python_interpreter(code: str, data: Any = None) -> str
```

**功能**: 在受控沙箱环境中执行 Python 代码进行数据分析

**参数**:
- `code`: 要执行的 Python 代码字符串
- `data`: 上一步工具返回的数据，代码中可通过变量访问

**返回值**: 代码执行的输出结果或错误信息

**支持的库和函数**:
- **数据分析**: pandas (别名 `pd`), numpy (别名 `np`), json
- **基础函数**: len, max, min, sum, range, enumerate, zip, sorted
- **数学函数**: abs, round
- **数据类型**: str, int, float, list, dict, tuple, set
- **其他**: print, locals, globals

**数据注入机制**:
- **DataFrame数据** → 注入为 `df` 变量
- **字典列表** → 自动转换为 `df` + 保留原始 `data`
- **包含'res'字段的字典** → 从 `data['res']` 创建 `df`
- **其他数据类型** → 注入为 `data` 变量

**重要规则**:
1. **必须**将最终结果赋值给 `result` 变量
2. 可使用 `print()` 输出中间结果
3. 支持复杂数据分析、统计计算、筛选等

**使用示例**:

```python
from src.tools.code_interpreter import python_interpreter
from src.tools.api import get_price_history

# 获取价格数据
price_data = get_price_history("600519")

# 数据统计分析
code = """
# 计算基本统计指标
avg_price = df['close'].mean()
max_volume = df['volume'].max()
recent_volatility = df['close'].pct_change().std()

# 趋势分析
ma20 = df['close'].rolling(20).mean()
current_price = df['close'].iloc[-1]
current_ma20 = ma20.iloc[-1]

trend = "上涨" if current_price > current_ma20 else "下跌"

# 生成报告
result = f'''
股票分析报告:
- 平均价格: {avg_price:.2f}
- 最大成交量: {max_volume:,}
- 当前价格: {current_price:.2f}
- 20日均线: {current_ma20:.2f}
- 趋势: {trend}
- 波动率: {recent_volatility:.4f}
'''
"""

analysis_result = python_interpreter(code, price_data)
print(analysis_result)
```

```python
# 高级筛选和分析
filter_code = """
# 筛选成交量异常的交易日
volume_mean = df['volume'].mean()
volume_std = df['volume'].std()
threshold = volume_mean + 2 * volume_std

abnormal_volume_days = df[df['volume'] > threshold]

# 分析这些异常日的价格变化
abnormal_returns = abnormal_volume_days['pct_change'].describe()

result = {
    "abnormal_days_count": len(abnormal_volume_days),
    "average_return_on_abnormal_days": abnormal_volume_days['pct_change'].mean(),
    "dates": abnormal_volume_days['date'].tolist()[-5:]  # 最近5个异常日
}
"""

abnormal_analysis = python_interpreter(filter_code, price_data)
```

---

### 7. stock_news_alt.py - 备用股票新闻 API

#### 7.1 备用新闻获取

```python
def get_stock_news(ticker: str) -> list
```

**功能**: 备用的美股新闻获取接口

**参数**:
- `ticker`: 美股代码（如 "AAPL", "TSLA"）

**返回数据**:
```python
[
    {
        'title': '新闻标题',
        'link': 'https://example.com/news',
        'publisher': '发布媒体',
        'time': 1703145600,  # Unix时间戳
        'text': '新闻正文内容'
    }
]
```

**使用示例**:
```python
from src.tools.stock_news_alt import get_stock_news

# 获取苹果公司新闻
news = get_stock_news("AAPL")
for item in news:
    print(f"标题: {item['title']}")
    print(f"发布者: {item['publisher']}")
```

---

## 🚀 综合使用示例

### 完整股票分析流程

```python
def comprehensive_stock_analysis(symbol: str, market_type: str = "cn"):
    """
    综合股票分析：财务指标 + 技术分析 + 新闻情感
    """
    from src.tools.api import get_financial_metrics, get_market_data, get_price_history
    from src.tools.news_crawler import get_stock_news, get_news_sentiment
    from src.tools.code_interpreter import python_interpreter
    
    print(f"开始分析股票: {symbol}")
    
    # 1. 获取基础数据
    print("📊 获取财务和市场数据...")
    financial_data = get_financial_metrics(symbol)
    market_data = get_market_data(symbol)
    price_data = get_price_history(symbol)
    
    # 2. 获取新闻和情感
    print("📰 获取新闻和情感分析...")
    news = get_stock_news(symbol, market_type=market_type, max_news=20)
    sentiment = get_news_sentiment(news, num_of_news=10)
    
    # 3. 技术分析代码
    technical_code = """
    # 计算关键技术指标
    current_price = df['close'].iloc[-1]
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    ma20 = df['close'].rolling(20).mean().iloc[-1]
    ma60 = df['close'].rolling(60).mean().iloc[-1]
    
    # 计算RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]
    
    # 波动率分析
    returns = df['close'].pct_change()
    volatility = returns.std() * (252 ** 0.5)  # 年化波动率
    
    # 趋势判断
    short_trend = "上涨" if current_price > ma5 else "下跌"
    medium_trend = "上涨" if ma5 > ma20 else "下跌"
    long_trend = "上涨" if ma20 > ma60 else "下跌"
    
    # RSI信号
    if current_rsi > 70:
        rsi_signal = "超买"
    elif current_rsi < 30:
        rsi_signal = "超卖"
    else:
        rsi_signal = "正常"
    
    result = {
        "current_price": round(current_price, 2),
        "ma5": round(ma5, 2),
        "ma20": round(ma20, 2),
        "ma60": round(ma60, 2),
        "rsi": round(current_rsi, 2),
        "volatility": round(volatility, 4),
        "short_trend": short_trend,
        "medium_trend": medium_trend,
        "long_trend": long_trend,
        "rsi_signal": rsi_signal
    }
    """
    
    print("📈 进行技术分析...")
    technical_analysis = python_interpreter(technical_code, price_data)
    
    # 4. 综合评分
    print("🔍 生成综合分析报告...")
    
    return {
        "symbol": symbol,
        "financial_metrics": financial_data,
        "market_data": market_data,
        "technical_analysis": technical_analysis,
        "news_sentiment": sentiment,
        "news_count": len(news),
        "recent_news": news[:3]  # 最近3条新闻
    }

# 使用示例
if __name__ == "__main__":
    # 分析贵州茅台
    result = comprehensive_stock_analysis("600519", "cn")
    
    # 分析苹果公司
    result_us = comprehensive_stock_analysis("AAPL", "us")
```

### AI 增强分析示例

```python
def ai_enhanced_analysis(symbol: str):
    """
    使用 AI 进行深度分析和投资建议
    """
    from src.tools.api import get_financial_metrics, get_price_history
    from src.tools.news_crawler import get_stock_news, get_news_sentiment
    from src.tools.openrouter_config import get_chat_completion
    
    # 收集数据
    financial_data = get_financial_metrics(symbol)
    price_data = get_price_history(symbol)
    news = get_stock_news(symbol, max_news=10)
    sentiment = get_news_sentiment(news)
    
    # 构建 AI 分析提示
    prompt = f"""
    请分析以下股票数据并给出投资建议：
    
    股票代码: {symbol}
    
    财务指标:
    - PE比率: {financial_data.get('pe_ratio', 'N/A')}
    - 市净率: {financial_data.get('price_to_book', 'N/A')}
    - ROE: {financial_data.get('return_on_equity', 'N/A')}
    - 营收增长率: {financial_data.get('revenue_growth', 'N/A')}
    
    技术面:
    - 当前价格: {price_data['close'].iloc[-1]:.2f}
    - 30日涨跌幅: {((price_data['close'].iloc[-1] / price_data['close'].iloc[-30] - 1) * 100):.2f}%
    
    新闻情感得分: {sentiment} (范围: -1到1)
    
    请从基本面、技术面、消息面三个维度分析，并给出明确的投资建议。
    """
    
    messages = [{"role": "user", "content": prompt}]
    ai_analysis = get_chat_completion(messages)
    
    return {
        "symbol": symbol,
        "ai_analysis": ai_analysis,
        "data_summary": {
            "pe_ratio": financial_data.get('pe_ratio'),
            "current_price": price_data['close'].iloc[-1],
            "news_sentiment": sentiment
        }
    }
```

---

## ⚠️ 注意事项

### 环境变量配置

在使用前请确保设置以下环境变量：

```bash
# Algogene API
export ALGOGENE_API_KEY="your_api_key"
export ALGOGENE_USER_ID="your_user_id"
export ALGOGENE_PROXY="http://127.0.0.1:7890"  # 可选

# LLM API
export GEMINI_API_KEY="your_gemini_key"
export OPENROUTER_API_KEY="your_openrouter_key"  # 可选
```

### 数据源说明

1. **A股数据**: 主要使用 akshare，备用雪球、东财
2. **美股数据**: 主要使用 yfinance，备用 Algogene
3. **加密货币**: 主要使用 yfinance，支持主流币种
4. **新闻数据**: A股使用 akshare，美股使用 yfinance + newspaper3k
5. **专业数据**: Algogene 提供期货、外汇、商品等

### 错误处理

所有 API 都包含错误处理机制：
- 网络超时重试
- 数据源切换
- 异常日志记录
- 默认值返回

### 性能优化

- 新闻数据有日级缓存机制
- 情感分析基于内容哈希缓存
- 建议批量调用时适当延迟

### 安全限制

- `code_interpreter` 在沙箱环境运行
- 禁止文件操作和网络访问
- 生产环境建议使用 Docker 隔离

---

## 📚 更多资源

- **测试文件**: `src/tools/tests/` 包含完整的单元测试
- **API 文档**: `src/tools/algogene/` 包含 Algogene API 详细文档
- **日志配置**: 使用 `src/utils/logging_config.py` 统一日志管理

---

*最后更新: 2025-01-15* 