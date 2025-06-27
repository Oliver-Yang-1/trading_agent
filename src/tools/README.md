# Tools 模块文档

本目录包含了交易系统所需的各种工具和API接口，为 agent 提供数据获取、分析和处理功能。

## 📁 目录结构

```
src/tools/
├── __init__.py                 # 工具模块初始化
├── openrouter_config.py        # LLM 客户端配置和封装
├── algogene_client.py          # Algogene API 客户端
├── api.py                      # 核心数据获取API
├── data_analyzer.py            # 股票数据技术分析工具
├── news_crawler.py             # 新闻爬虫和情感分析
└── test_*.py                   # 测试文件
```

## 🔧 核心模块

### 1. openrouter_config.py - LLM 客户端配置

提供统一的 LLM 客户端封装，支持多种 AI 模型。

#### 主要函数

```python
def get_chat_completion(messages, model=None, max_retries=3, initial_retry_delay=1,
                        client_type="auto", api_key=None, base_url=None) -> str
```

**功能**: 获取聊天完成结果，包含重试逻辑

**参数**:
- `messages`: 消息列表，OpenAI 格式
- `model`: 模型名称（可选）
- `max_retries`: 最大重试次数，默认3次
- `initial_retry_delay`: 初始重试延迟（秒），默认1秒
- `client_type`: 客户端类型，支持 "auto", "gemini", "openai_compatible"
- `api_key`: API 密钥（可选）
- `base_url`: API 基础 URL（可选）

**返回值**: 
- `str`: 模型回答内容，出错时返回 None

**使用示例**:
```python
from src.tools.openrouter_config import get_chat_completion

messages = [
    {"role": "user", "content": "分析一下这只股票的技术面"}
]
response = get_chat_completion(messages)
```

### 2. algogene_client.py - Algogene API 客户端

专业的金融数据 API 客户端，提供历史价格和实时报价数据。

#### AlgogeneClient 类

**初始化**:
```python
client = AlgogeneClient()
```

**环境变量要求**:
- `ALGOGENE_API_KEY`: 您的 API 密钥
- `ALGOGENE_USER_ID`: 您的用户 ID

#### 主要方法

##### get_price_history()

```python
def get_price_history(count: int, instrument: str, interval: str, timestamp: str) -> Dict[str, Any]
```

**功能**: 获取历史价格数据

**参数**:
- `count`: 数据点数量
- `instrument`: 交易工具符号
- `interval`: 时间间隔
- `timestamp`: 参考时间戳

**返回数据结构**:
```python
{
    "res": [
        {
            "t": "2023-12-01 09:30:00",    # 时间戳
            "o": 100.0,                    # 开盘价
            "h": 105.0,                    # 最高价
            "l": 99.0,                     # 最低价
            "c": 102.0,                    # 收盘价
            "b": 101.5,                    # 买价
            "a": 102.5,                    # 卖价
            "m": 102.0,                    # 中位价
            "v": 1000,                     # 成交量
            "instrument": "GOOGL"          # 工具名称
        }
    ],
    "count": 1
}
```

##### get_realtime_price()

```python
def get_realtime_price(symbols: str, broker: Optional[str] = None) -> Dict[str, Any]
```

**功能**: 获取实时市场数据

**参数**:
- `symbols`: 金融符号列表，用逗号分隔
- `broker`: 特定经纪商，支持 'diginex', 'exness', 'ib', 'ig', 'oanda'

**使用示例**:
```python
from src.tools.algogene_client import AlgogeneClient

client = AlgogeneClient()

# 获取历史数据
history = client.get_price_history(
    count=5,
    instrument="GOOGL",
    interval="M",
    timestamp="2025-05-31 00:00:00"
)

# 获取实时数据
realtime = client.get_realtime_price(symbols="BTCUSD")
```

### 3. api.py - 核心数据获取API

提供 A股市场数据获取的核心功能，是系统的数据引擎。

#### 主要函数

##### get_financial_metrics()

```python
def get_financial_metrics(symbol: str) -> Dict[str, Any]
```

**功能**: 获取股票的财务指标数据

**参数**:
- `symbol`: 股票代码（如 "600519"）

**返回的指标**:
```python
{
    # 盈利能力指标
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
    "free_cash_flow_per_share": 5.2,   # 每股经营性现金流
    "earnings_per_share": 8.5,         # 每股收益
    
    # 估值比率
    "pe_ratio": 25.0,                  # 市盈率
    "price_to_book": 3.0,              # 市净率
    "price_to_sales": 2.5              # 市销率
}
```

##### get_financial_statements()

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
    },
    {  # 上一期间
        # ... 同样结构
    }
]
```

##### get_market_data()

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

##### get_price_history()

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
from src.tools.api import get_financial_metrics, get_price_history

# 获取财务指标
metrics = get_financial_metrics("600519")
print(f"PE比率: {metrics['pe_ratio']}")

# 获取历史价格
df = get_price_history("600519", "2023-01-01", "2023-12-31")
print(f"数据记录数: {len(df)}")
```

### 4. data_analyzer.py - 股票数据技术分析工具

提供股票技术分析功能，计算各种技术指标。

#### 主要函数

##### analyze_stock_data()

```python
def analyze_stock_data(symbol: str, start_date: str = None, end_date: str = None)
```

**功能**: 获取股票历史数据并计算技术指标，保存为CSV文件

**计算的技术指标**:
- **移动平均线**: MA5, MA10, MA20, MA60
- **MACD**: MACD线、信号线、MACD柱状图
- **RSI**: 相对强弱指数（14期）
- **布林带**: 上轨、中轨、下轨
- **成交量指标**: 成交量移动平均、成交量比率
- **动量指标**: 价格动量、价格加速度
- **波动率指标**: 日收益率、5日/20日波动率

**使用示例**:
```python
from src.tools.data_analyzer import analyze_stock_data

# 分析贵州茅台过去一年的数据
analyze_stock_data("600519", "2023-01-01", "2023-12-31")
```

### 5. news_crawler.py - 新闻爬虫和情感分析

提供股票新闻获取和情感分析功能。

#### 主要函数

##### get_stock_news()

```python
def get_stock_news(symbol: str, max_news: int = 10) -> list
```

**功能**: 获取并处理个股新闻

**参数**:
- `symbol`: 股票代码
- `max_news`: 获取的新闻条数，默认10条，最大100条

**返回数据结构**:
```python
[
    {
        "title": "新闻标题",
        "content": "新闻内容",
        "publish_time": "2023-12-01 10:30:00",
        "source": "财经网站",
        "url": "https://example.com/news/123",
        "keyword": "关键词"
    }
]
```

##### get_news_sentiment()

```python
def get_news_sentiment(news_list: list, num_of_news: int = 5) -> float
```

**功能**: 分析新闻情感得分

**参数**:
- `news_list`: 新闻列表
- `num_of_news`: 用于分析的新闻数量，默认5条

**返回值**: 
- `float`: 情感得分，范围 [-1, 1]
  - 1: 极其积极（重大利好）
  - 0.5-0.9: 积极（业绩增长、获得订单等）
  - 0: 中性（日常公告等）
  - -0.5--0.9: 消极（业绩下滑等）
  - -1: 极其消极（重大违规等）

**使用示例**:
```python
from src.tools.news_crawler import get_stock_news, get_news_sentiment

# 获取新闻
news = get_stock_news("600519", max_news=10)

# 分析情感
sentiment = get_news_sentiment(news, num_of_news=5)
print(f"新闻情感得分: {sentiment}")
```

## 🔧 使用建议

### Agent 调用示例

```python
# 为某只股票获取完整的分析数据
def get_complete_stock_analysis(symbol: str):
    from src.tools.api import get_financial_metrics, get_market_data, get_price_history
    from src.tools.news_crawler import get_stock_news, get_news_sentiment
    
    # 获取财务数据
    metrics = get_financial_metrics(symbol)
    market_data = get_market_data(symbol)
    
    # 获取价格数据
    price_data = get_price_history(symbol, adjust="qfq")
    
    # 获取新闻和情感
    news = get_stock_news(symbol, max_news=10)
    sentiment = get_news_sentiment(news)
    
    return {
        "financial_metrics": metrics,
        "market_data": market_data,
        "price_data": price_data,
        "news": news,
        "sentiment": sentiment
    }
```

### 缓存机制

- **新闻数据**: 自动缓存当日获取的新闻，避免重复请求
- **情感分析**: 缓存分析结果，相同新闻组合不重复分析
- **文件位置**: `src/data/` 目录下

### 错误处理

所有函数都包含完善的错误处理机制：
- 网络请求失败时的重试逻辑
- 数据解析错误时的默认值返回
- 详细的日志记录便于调试

### 环境变量配置

在项目根目录的 `.env` 文件中配置：

```env
# Algogene API
ALGOGENE_API_KEY=your_api_key
ALGOGENE_USER_ID=your_user_id

# LLM API (用于情感分析)
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
```

## 📝 注意事项

1. **数据源依赖**: 主要依赖 akshare 库获取A股数据
2. **网络环境**: 部分API可能需要特定网络环境
3. **频率限制**: 注意各API的调用频率限制
4. **数据质量**: 获取数据后建议进行数据质量检查
5. **时区处理**: 时间数据均使用北京时间

## 🔄 更新维护

- 定期检查数据源API的变化
- 更新技术指标计算逻辑
- 优化缓存机制和错误处理
- 扩展新的数据源和分析功能 