# Tools Module - AI Trading System Core Tools

这个模块为AI交易系统提供核心工具和API接口，包括数据获取、分析处理、AI集成等功能。系统采用模块化设计，支持多数据源、多AI服务集成。

## 📁 目录结构与架构

```
src/tools/
├── __init__.py                 # 工具模块初始化
├── openrouter_config.py        # LLM服务统一封装 (Level 1)
├── algogene_client.py          # 国际金融数据API客户端 (Level 1)  
├── code_interpreter.py         # Python代码执行器 (Level 1)
├── api.py                      # A股核心数据接口 (Level 2)
├── news_crawler.py             # 新闻爬取与情感分析 (Level 2)
├── data_analyzer.py            # 股票技术分析工具 (Level 3)
└── test_*.py                   # 测试文件集合
```

### 依赖层次架构

```
Level 1 - 基础工具层 (无内部依赖)
├── openrouter_config.py    # LLM服务统一接口
├── algogene_client.py      # 专业金融数据API
└── code_interpreter.py     # 代码执行沙箱

Level 2 - 组合工具层 (依赖Level 1)
├── api.py                  # A股数据核心引擎
└── news_crawler.py         # 新闻+情感分析 (依赖LLM)

Level 3 - 高级工具层 (依赖Level 1+2)
└── data_analyzer.py        # 技术分析 (依赖api.py)
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

### 5. code_interpreter.py - Python代码执行器

提供安全的Python代码执行环境，支持数据分析和处理。

#### 主要函数

##### python_interpreter()

```python
def python_interpreter(code: str, data: Any = None) -> str
```

**功能**: 在受控沙箱环境中执行Python代码进行数据分析

**参数**:
- `code`: 要执行的Python代码字符串
- `data`: 上一步工具返回的数据，代码中可通过变量访问

**返回值**: 代码执行的输出结果或错误信息

**支持的库和函数**:
- pandas (别名 pd), numpy (别名 np), json
- 基础函数: len, max, min, sum, range等
- 数学函数: abs, round等
- 数据类型: str, int, float, list, dict等

**数据注入机制**:
- DataFrame数据 → `df` 变量
- 字典列表 → 自动转换为 `df` + 保留 `data`
- 包含'res'字段的字典 → 从'res'创建 `df`
- 其他数据类型 → `data` 变量

**使用规则**:
1. **必须**将最终结果赋值给 `result` 变量
2. 可使用 `print()` 输出中间结果
3. 支持复杂数据分析、统计计算、筛选等

**使用示例**:
```python
from src.tools.code_interpreter import python_interpreter

# 数据统计分析
code = """
avg_price = df['close'].mean()
max_volume = df['volume'].max()
result = f"平均价格: {avg_price:.2f}, 最大成交量: {max_volume}"
"""

result = python_interpreter(code, price_data)
print(result)
```

### 6. news_crawler.py - 新闻爬虫和情感分析

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

## 🏗️ 系统集成架构

### 多数据源集成

```
中国A股数据源:
├── akshare (主要) → api.py → agents
├── Sina Finance → news_crawler.py → sentiment analysis
└── 雪球/东财 → 备用数据源

国际市场数据源:
├── Algogene API → algogene_client.py → global markets
├── yfinance → 备用国际数据
└── Interactive Brokers → 专业交易数据

AI服务集成:
├── Gemini API (主要) → openrouter_config.py → LLM reasoning
├── OpenAI Compatible APIs → 备用LLM服务
└── LangChain → AI application framework
```

### 依赖关系图

```
外部服务依赖:
├── akshare → (api.py, news_crawler.py, data_analyzer.py)
├── Gemini/OpenAI → (openrouter_config.py) → (news_crawler.py)
├── Algogene → (algogene_client.py)
└── pandas/numpy → (所有数据处理模块)

内部模块依赖:
openrouter_config.py (无依赖)
├── news_crawler.py (依赖LLM接口)
└── code_interpreter.py (可选LLM增强)

api.py (无内部依赖)
└── data_analyzer.py (依赖price history)

algogene_client.py (独立模块)
code_interpreter.py (独立执行器)
```

### 错误处理与容错机制

**网络请求容错**:
- 指数退避重试机制
- 多数据源切换
- 连接超时处理
- 请求频率限制

**数据处理容错**:
- 空数据默认值处理
- 数据格式验证
- pandas DataFrame安全转换
- JSON序列化异常处理

**API调用容错**:
- LLM服务降级
- 缓存机制减少重复调用
- 配置文件缺失处理
- 环境变量验证

## 🔧 使用指南

### 工具集成使用模式

#### 1. 数据驱动分析流程

```python
# 完整股票分析流程
def comprehensive_stock_analysis(symbol: str):
    from src.tools.api import get_financial_metrics, get_market_data, get_price_history
    from src.tools.news_crawler import get_stock_news, get_news_sentiment
    from src.tools.code_interpreter import python_interpreter
    
    # 步骤1: 获取基础数据
    financial_data = get_financial_metrics(symbol)
    market_data = get_market_data(symbol)
    price_data = get_price_history(symbol)
    
    # 步骤2: 获取新闻和情感
    news = get_stock_news(symbol, max_news=15)
    sentiment = get_news_sentiment(news, num_of_news=10)
    
    # 步骤3: 动态代码分析
    analysis_code = """
    # 计算技术指标
    latest_price = df['close'].iloc[-1]
    ma20 = df['close'].rolling(20).mean().iloc[-1]
    volatility = df['close'].pct_change().std() * np.sqrt(252)
    
    # 趋势分析
    price_trend = "上涨" if latest_price > ma20 else "下跌"
    risk_level = "高" if volatility > 0.3 else "中" if volatility > 0.2 else "低"
    
    result = {
        "current_price": latest_price,
        "ma20": ma20,
        "trend": price_trend,
        "volatility": volatility,
        "risk_level": risk_level
    }
    """
    
    technical_analysis = python_interpreter(analysis_code, price_data)
    
    return {
        "financial_metrics": financial_data,
        "market_data": market_data,
        "technical_analysis": technical_analysis,
        "news_sentiment": sentiment,
        "raw_news": news[:5]  # 只返回前5条新闻
    }
```

#### 2. AI增强分析模式

```python
# AI驱动的动态分析
def ai_enhanced_analysis(symbol: str, custom_query: str):
    from src.tools.openrouter_config import get_chat_completion
    from src.tools.api import get_price_history
    from src.tools.code_interpreter import python_interpreter
    
    # 获取数据
    price_data = get_price_history(symbol)
    
    # AI生成分析代码
    ai_prompt = f"""
    基于用户查询: {custom_query}
    请生成Python代码来分析股票{symbol}的数据。
    数据存在df变量中，包含价格、成交量等信息。
    代码必须将结果赋值给result变量。
    """
    
    generated_code = get_chat_completion([
        {"role": "user", "content": ai_prompt}
    ])
    
    # 执行AI生成的代码
    analysis_result = python_interpreter(generated_code, price_data)
    
    return {
        "query": custom_query,
        "generated_code": generated_code,
        "analysis_result": analysis_result
    }
```

#### 3. 多市场数据对比

```python
# 对比分析A股与国际市场
def cross_market_analysis(a_stock: str, us_stock: str):
    from src.tools.api import get_price_history as get_a_stock_data
    from src.tools.algogene_client import get_algogene_price_history
    from src.tools.code_interpreter import python_interpreter
    
    # 获取A股数据
    a_data = get_a_stock_data(a_stock)
    
    # 获取美股数据
    us_data = get_algogene_price_history(
        count=100,
        instrument=us_stock,
        interval="D",
        timestamp="2024-01-01 00:00:00"
    )
    
    # 对比分析代码
    comparison_code = """
    # 处理美股数据
    us_df = pd.DataFrame(us_data['res']) if 'res' in us_data else pd.DataFrame()
    
    if not us_df.empty and not df.empty:
        # 计算相关性和对比指标
        a_returns = df['close'].pct_change().dropna()
        us_returns = us_df['c'].pct_change().dropna()
        
        # 对齐数据长度
        min_length = min(len(a_returns), len(us_returns))
        correlation = a_returns.tail(min_length).corr(us_returns.tail(min_length))
        
        result = {
            "correlation": correlation,
            "a_stock_volatility": a_returns.std(),
            "us_stock_volatility": us_returns.std(),
            "comparison": "高相关" if abs(correlation) > 0.7 else "低相关"
        }
    else:
        result = {"error": "数据获取失败"}
    """
    
    comparison_result = python_interpreter(comparison_code, a_data)
    
    return comparison_result
```

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

### 缓存与性能优化

#### 智能缓存策略

**文件缓存**:
- 新闻数据: `src/data/stock_news/{symbol}_news.json` (日级缓存)
- 情感分析: `src/data/sentiment_cache.json` (内容哈希缓存)
- 宏观分析: 按agent模块分别缓存

**缓存失效机制**:
- 新闻数据: 每日自动更新
- 情感分析: 基于新闻内容组合的唯一标识
- 价格数据: 实时获取，不缓存
- 财务数据: 可考虑季度缓存

**性能优化建议**:
```python
# 批量数据获取
def batch_analysis(symbols: list):
    results = {}
    for symbol in symbols:
        try:
            # 利用缓存机制，重复调用会使用缓存
            results[symbol] = get_stock_news(symbol, max_news=5)
        except Exception as e:
            results[symbol] = {"error": str(e)}
    return results
```

### 错误处理与调试

#### 分层错误处理

**Level 1 - 网络层错误**:
```python
# 重试机制示例 (openrouter_config.py)
@backoff.on_exception(
    backoff.expo,
    (Exception),
    max_tries=5,
    max_time=300
)
def api_call_with_retry(...):
    # API调用逻辑
```

**Level 2 - 数据层错误**:
```python
# 安全数据处理 (api.py)
def safe_float(value, default=0.0):
    try:
        return float(value) if value and str(value).strip() != '-' else default
    except:
        return default
```

**Level 3 - 应用层错误**:
```python
# 代码执行错误处理 (code_interpreter.py)
try:
    exec(code, sandbox_globals, sandbox_locals)
except Exception as e:
    return f"代码执行出错: {str(e)}\n详细错误:\n{traceback.format_exc()}"
```

#### 日志系统

**日志级别配置**:
- ERROR: API调用失败、数据解析错误
- WARNING: 数据质量问题、缓存失效
- INFO: 正常操作流程、数据获取成功
- DEBUG: 详细的数据内容、请求参数

**调试技巧**:
```python
# 启用详细日志
import logging
logging.getLogger('api').setLevel(logging.DEBUG)
logging.getLogger('news_crawler').setLevel(logging.DEBUG)

# 数据质量检查
def validate_data_quality(df):
    issues = []
    if df.isna().sum().any():
        issues.append(f"发现NaN值: {df.isna().sum().to_dict()}")
    if len(df) < 100:
        issues.append(f"数据量不足: {len(df)}条")
    return issues
```

### 配置管理

#### 环境变量配置

在项目根目录的 `.env` 文件中配置：

```env
# === AI/LLM服务配置 ===
# 主要LLM服务 (Gemini)
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash

# 备用LLM服务 (OpenAI Compatible)
OPENAI_COMPATIBLE_API_KEY=your_openai_key
OPENAI_COMPATIBLE_BASE_URL=https://api.openai.com/v1
OPENAI_COMPATIBLE_MODEL=gpt-3.5-turbo

# === 金融数据服务 ===
# 专业金融数据 (Algogene)
ALGOGENE_API_KEY=your_algogene_key
ALGOGENE_USER_ID=your_user_id

# === 可选配置 ===
# 日志级别
LOG_LEVEL=INFO

# 缓存设置
CACHE_ENABLED=true
CACHE_EXPIRE_HOURS=24
```

#### 配置验证

```python
# 配置检查脚本
def validate_configuration():
    import os
    required_configs = {
        'GEMINI_API_KEY': '主要LLM服务',
        'ALGOGENE_API_KEY': 'Algogene金融数据',
        'ALGOGENE_USER_ID': 'Algogene用户ID'
    }
    
    missing = []
    for config, description in required_configs.items():
        if not os.getenv(config):
            missing.append(f"{config} ({description})")
    
    if missing:
        print("❌ 缺少必要配置:")
        for item in missing:
            print(f"   - {item}")
        return False
    
    print("✅ 配置验证通过")
    return True
```

#### 动态配置切换

```python
# 根据环境自动选择服务
def get_optimal_llm_client():
    if os.getenv('GEMINI_API_KEY'):
        return get_chat_completion(messages, client_type="gemini")
    elif os.getenv('OPENAI_COMPATIBLE_API_KEY'):
        return get_chat_completion(messages, client_type="openai_compatible")
    else:
        raise ValueError("未配置任何LLM服务")
```

## ⚠️ 重要注意事项

### 数据源与依赖风险

**高风险依赖**:
- `akshare`: A股数据核心来源，API变更可能影响核心功能
- `Gemini API`: 情感分析主要服务，配额限制可能影响分析

**中风险依赖**:
- `雪球/东财接口`: 备用数据源，稳定性一般
- `Sina Finance`: 新闻数据源，可能有反爬虫机制

**低风险依赖**:
- `pandas/numpy`: 成熟的数据处理库
- `requests`: HTTP请求库，稳定可靠

### 使用限制与建议

**API调用频率**:
- akshare: 建议间隔1-2秒
- Gemini API: 注意RPM限制
- Algogene: 按套餐限制调用

**网络环境要求**:
- Gemini API: 可能需要海外网络环境
- 部分数据源: 建议国内网络环境
- 代理设置: 支持HTTP/HTTPS代理

**数据质量保证**:
```python
# 数据验证示例
def validate_price_data(df):
    checks = {
        "数据完整性": len(df) > 0,
        "价格合理性": df['close'].between(0.01, 10000).all(),
        "成交量合理性": df['volume'].ge(0).all(),
        "日期连续性": df['date'].is_monotonic_increasing
    }
    
    failed_checks = [k for k, v in checks.items() if not v]
    if failed_checks:
        print(f"⚠️ 数据质量问题: {', '.join(failed_checks)}")
    
    return len(failed_checks) == 0
```

**时区处理**:
- A股数据: 北京时间 (UTC+8)
- 国际数据: GMT+0 (需要转换)
- 时间戳格式: 统一使用 "YYYY-MM-DD HH:MM:SS"

### 安全注意事项

**代码执行安全** (`code_interpreter.py`):
- 沙箱环境限制了可用函数
- 禁止文件操作和网络访问
- 禁止导入未授权的模块
- 建议生产环境使用Docker隔离

**API密钥安全**:
- 不要将密钥硬编码在代码中
- 使用环境变量或密钥管理服务
- 定期轮换API密钥
- 监控API使用情况

## 🔄 维护与扩展

### 定期维护任务

**月度检查**:
- [ ] akshare库版本更新和兼容性测试
- [ ] API接口稳定性测试
- [ ] 缓存文件清理和优化
- [ ] 错误日志分析和处理

**季度更新**:
- [ ] 技术指标计算逻辑优化
- [ ] 新数据源评估和集成
- [ ] 性能基准测试
- [ ] 安全漏洞扫描

**年度升级**:
- [ ] 依赖库大版本升级
- [ ] 架构重构和优化
- [ ] 新AI模型集成测试
- [ ] 完整的功能回归测试

### 扩展开发指南

#### 添加新数据源

```python
# 1. 创建新的客户端文件
# src/tools/new_data_source.py

class NewDataClient:
    def __init__(self):
        self.api_key = os.getenv('NEW_API_KEY')
    
    def get_data(self, symbol: str):
        # 实现数据获取逻辑
        pass

# 2. 在api.py中集成备用数据源
def get_financial_metrics_enhanced(symbol: str):
    try:
        return get_financial_metrics(symbol)  # 主要数据源
    except Exception:
        return new_data_client.get_data(symbol)  # 备用数据源
```

#### 添加新AI服务

```python
# 1. 在openrouter_config.py中添加新客户端
class NewLLMClient:
    def get_completion(self, messages):
        # 实现新LLM服务调用
        pass

# 2. 更新客户端工厂
def create_llm_client(client_type):
    if client_type == "new_llm":
        return NewLLMClient()
    # ... 其他客户端
```

#### 添加新分析工具

```python
# 1. 创建新工具文件
# src/tools/advanced_analyzer.py

def deep_learning_analysis(data):
    """使用深度学习进行高级分析"""
    # 实现分析逻辑
    pass

# 2. 在super_node.py中注册新工具
AVAILABLE_TOOLS.update({
    "deep_learning_analysis": {
        "function": deep_learning_analysis,
        "description": "深度学习股票分析",
        "parameters": ["data: 股票数据"]
    }
})
```

### 测试覆盖完善

**缺失的测试模块**:
```python
# test_api.py - API数据获取测试
def test_financial_metrics():
    result = get_financial_metrics("600519")
    assert isinstance(result, list)
    assert len(result) > 0

# test_algogene.py - Algogene API测试  
def test_price_history():
    result = get_algogene_price_history(5, "AAPL", "D", "2024-01-01 00:00:00")
    assert "res" in result

# test_code_interpreter.py - 代码执行测试
def test_pandas_operations():
    code = "result = df['close'].mean()"
    test_data = pd.DataFrame({'close': [100, 110, 120]})
    result = python_interpreter(code, test_data)
    assert "110" in result
```

### 性能监控

```python
# 性能监控装饰器
import time
from functools import wraps

def performance_monitor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        # 记录到监控系统
        logger.info(f"{func.__name__} 执行时间: {duration:.2f}秒")
        
        return result
    return wrapper

# 使用示例
@performance_monitor
def get_price_history(symbol, start_date, end_date):
    # 原有实现
    pass
```

---

💡 **开发建议**: 保持工具模块的独立性和可测试性，新增功能时优先考虑向后兼容性和错误处理机制。 