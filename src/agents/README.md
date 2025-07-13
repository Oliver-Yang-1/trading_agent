# Agents Module - AI Trading Agent System

这个模块包含了一个完整的多agent AI交易系统，使用LangGraph进行agent编排，通过多个专业化的智能代理协同工作来分析股票并做出交易决策。

## 系统架构

### 工作流程图

```
数据获取层:
├── market_data_agent      # 市场数据收集
└── macro_news_agent       # 宏观新闻分析
           │
           ▼
并行分析层:
├── technical_analyst_agent    # 技术分析
├── fundamentals_agent         # 基本面分析
├── sentiment_agent           # 情感分析
├── valuation_agent          # 估值分析
└── macro_analyst_agent      # 宏观分析
           │
           ▼
研究合成层:
├── researcher_bull_agent     # 多方研究员
└── researcher_bear_agent     # 空方研究员
           │
           ▼
辩论决策层:
├── debate_room_agent        # 辩论室
├── risk_management_agent    # 风险管理
└── portfolio_management_agent # 投资组合管理
```

## 核心文件说明

### 状态管理

#### `state.py`
- **功能**: 系统核心的状态管理模块
- **核心类**: `AgentState` - 定义所有agent之间的共享状态结构
- **关键函数**:
  - `merge_dicts()` - 合并字典数据
  - `show_workflow_status()` - 显示工作流状态
  - **依赖**: 无（基础模块）

### 数据收集层 (Layer 1)

#### `market_data.py`
- **功能**: 市场数据收集，负责获取股价历史、财务指标和市场信息
- **数据源**: akshare API
- **输出**: 价格历史、财务指标、财务报表、市场数据
- **依赖**: `src.tools.api` (get_financial_metrics, get_financial_statements等)
- **API装饰器**: `@agent_endpoint("market_data")`

#### `macro_news_agent.py`
- **功能**: 宏观新闻代理，获取CSI 300指数新闻并进行宏观分析
- **数据源**: 新浪财经新闻API
- **输出**: 宏观经济新闻及LLM分析结果
- **特色**: 日级缓存机制，避免重复API调用
- **依赖**: `news_crawler`, `openrouter_config`
- **API装饰器**: `@agent_endpoint("macro_news")`

### 并行分析层 (Layer 2)

#### `technicals.py`
- **功能**: 技术分析师，提供多策略技术分析
- **分析策略**:
  - 趋势跟踪 (Trend Following)
  - 均值回归 (Mean Reversion)
  - 动量策略 (Momentum)
  - 波动率策略 (Volatility)
  - 统计套利 (Statistical Arbitrage)
- **依赖**: `market_data_agent` 的价格数据
- **API装饰器**: `@agent_endpoint("technical_analyst")`

#### `fundamentals.py`
- **功能**: 基本面分析师，分析财务指标
- **分析维度**:
  - 盈利能力 (Profitability)
  - 增长性 (Growth)
  - 财务健康 (Financial Health)
  - 估值比率 (Valuation Ratios)
- **依赖**: `market_data_agent` 的财务数据
- **API装饰器**: `@agent_endpoint("fundamentals_analyst")`

#### `sentiment.py`
- **功能**: 情感分析师，分析股票相关新闻情感
- **分析范围**: 最近7天的新闻
- **输出**: 新闻情感评分和分析
- **依赖**: `news_crawler` (get_stock_news, get_news_sentiment)
- **API装饰器**: `@agent_endpoint("sentiment_analyst")`

#### `valuation.py`
- **功能**: 估值分析师，使用多种方法评估内在价值
- **估值方法**:
  - DCF (现金流折现法)
  - 所有者收益法 (Owner Earnings Method)
- **依赖**: `market_data_agent` 的财务数据
- **API装饰器**: `@agent_endpoint("valuation_analyst")`

#### `macro_analyst.py`
- **功能**: 宏观分析师，分析宏观经济环境对个股的影响
- **分析内容**: 结合宏观新闻和个股基本面，评估宏观影响
- **特色**: 文件缓存机制
- **依赖**: `macro_news_agent`, `fundamentals_agent`
- **API装饰器**: `@agent_endpoint("macro_analyst")`

### 研究合成层 (Layer 3)

#### `researcher_bull.py`
- **功能**: 多方研究员，从看多角度分析市场数据
- **输入**: 汇总所有分析层的结果
- **输出**: 看多论点和置信度评分
- **依赖**: 所有分析层agent的输出
- **API装饰器**: `@agent_endpoint("researcher_bull")`

#### `researcher_bear.py`
- **功能**: 空方研究员，从看空角度分析市场数据
- **输入**: 汇总所有分析层的结果
- **输出**: 看空论点和置信度评分
- **依赖**: 所有分析层agent的输出
- **API装饰器**: `@agent_endpoint("researcher_bear")`

### 辩论决策层 (Layer 4)

#### `debate_room.py`
- **功能**: 辩论室，综合多空观点并引入LLM进行第三方分析
- **核心算法**: 混合置信度差异 (70%原始观点 + 30%LLM分析)
- **输出**: 最终投资信号 (BUY/SELL/HOLD)
- **依赖**: `researcher_bull_agent`, `researcher_bear_agent`
- **API装饰器**: `@agent_endpoint("debate_room")`

#### `risk_manager.py`
- **功能**: 风险管理，评估投资风险并提供风险调整建议
- **风险指标**: 
  - 波动率评估
  - 下行风险计算
  - 压力测试
  - 仓位建议
- **依赖**: `debate_room_agent` 的信号
- **API装饰器**: `@agent_endpoint("risk_management")`

#### `portfolio_manager.py`
- **功能**: 投资组合管理，做出最终交易决策
- **决策过程**: 汇总所有agent结果，调用LLM做最终交易决策
- **输出**: 具体交易行动 (买入/卖出/持有)
- **依赖**: 所有前置agent的输出
- **API装饰器**: `@agent_endpoint("portfolio_management")`

### 增强模块

#### `super_node.py`
- **功能**: 增强Agent，实现ReAct (Reasoning-Acting) 能力
- **特色**: 
  - 支持推理-行动循环
  - 集成多种工具调用
  - 代码解释器支持
  - 动态工具选择
- **工具集成**: 
  - 金融数据API
  - 新闻爬虫
  - Python代码解释器
  - Algogene数据源
- **依赖**: 广泛的工具模块集成
- **API装饰器**: `@agent_endpoint("super_node")`

## 依赖关系详解

### 状态传递机制
- **AgentState**: 所有agent共享的状态对象
- **数据共享**: 通过 `state["data"]` 传递分析数据
- **消息系统**: 通过 `state["messages"]` 传递分析结果
- **元数据**: 通过 `state["metadata"]` 传递控制信息

### 层级依赖
1. **第1层** → **第2层**: 市场数据为所有分析提供基础
2. **第2层** → **第3层**: 分析结果供研究员综合
3. **第3层** → **第4层**: 研究观点供决策层使用
4. **第4层内部**: 辩论 → 风险管理 → 投资决策

### 外部依赖
- **数据源**: akshare, 新浪财经, Algogene
- **AI服务**: OpenRouter/Gemini API
- **工具模块**: `src.tools.*`
- **配置模块**: `src.utils.*`

## API集成

每个agent都通过装饰器 `@agent_endpoint` 暴露REST API接口，支持：
- 独立agent调用
- 完整工作流执行
- 实时状态查询
- 推理过程展示

## 使用方式

### 命令行模式
```bash
# 完整分析
poetry run python src/main.py --ticker 000001

# 显示推理过程
poetry run python src/main.py --ticker 000001 --show-reasoning
```

### API模式
```bash
# 启动API服务
poetry run python run_with_backend.py

# 调用特定agent
curl -X POST http://localhost:8000/api/agents/technical_analyst
```

### 超级节点模式
```python
# 使用ReAct模式进行自定义分析
super_node_agent(state_with_custom_query)
```

## 配置与扩展

### 添加新Agent
1. 继承基础state管理
2. 实现agent函数
3. 添加API装饰器
4. 集成到工作流图

### 自定义分析
- 修改各层agent的分析逻辑
- 调整置信度计算方式
- 扩展数据源集成
- 优化决策算法

## 日志与监控

- 每个agent都有独立的日志器
- LLM交互完整记录
- 工作流状态实时跟踪
- 错误处理和降级机制

---

这个多agent系统实现了一个完整的AI驱动量化交易决策流水线，从数据获取到最终交易决策，每个环节都有专门的智能代理负责，通过协同工作实现智能投资决策。