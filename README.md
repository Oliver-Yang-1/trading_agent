<div align="center">

# 🤖 AI Investment System 🧠

</div>

## Project Overview

This is a proof-of-concept project for an artificial intelligence-based investment system. The project aims to explore how AI can assist investment decisions through multi-agent collaboration, combining the analytical capabilities of Large Language Models (LLMs) to provide multi-perspective market interpretations and investment advice.

### Core Concept: Multi-Agent Collaboration and LLM-Enhanced Decision Making

The system simulates different roles of researchers (bull, bear) and analysts, collecting information, analyzing, debating, and ultimately forming investment decisions. The latest "Debate Room Intelligence Enhancement" mechanism introduces LLM as an independent third party, further improving the objectivity and comprehensiveness of decisions.

## System Architecture

The new version of the architecture has made the following improvements:

1. Introduced Researcher Bull and Researcher Bear, allowing the system to analyze the market from different perspectives
2. Added a Debate Room process, achieving more comprehensive decisions through debates between bull and bear parties
3. Optimized data flow, making the decision process more systematic and complete

Additionally, the terminal output has been optimized, reducing unnecessary detailed data display, making the output clearer and easier to read.

## 🛠️ Installation and Setup

First, clone this repository to your local machine.

### 1. Install Poetry

Poetry is a tool for Python dependency management and packaging.

**Windows (PowerShell):**

```powershell
(Invoke-WebRequest -Uri [https://install.python-poetry.org](https://install.python-poetry.org) -UseBasicParsing).Content | py -
```

**Unix/macOS:**

```bash
curl -sSL [https://install.python-poetry.org](https://install.python-poetry.org) | python3 -
```

### 2. Install Project Dependencies

Use Poetry to install the required project dependencies:

```bash
poetry lock --no-update
```

```bash
poetry install
```

### 3. Configure Environment Variables

Environment variables are used to store sensitive information such as API keys.

First, copy the example environment variable file:

```bash
# Create .env file for your API keys
cp .env.example .env
```

Then, you can get your Gemini API key: [Google AI Studio](https://aistudio.google.com/)

You can set environment variables in two ways:

**a. Directly modify the `.env` file (recommended)**
Open the `.env` file in the project root directory and enter your API key:

```env
# Gemini API Configuration
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-flash

# OpenAI Compatible API Configuration (optional)
OPENAI_COMPATIBLE_API_KEY=your-openai-compatible-api-key
OPENAI_COMPATIBLE_BASE_URL=https://your-api-endpoint.com/v1
OPENAI_COMPATIBLE_MODEL=your-model-name
```

**Note:** The system will prioritize using the OpenAI Compatible API (if configured), otherwise it will use the Gemini API.

**b. Set via command line**

**Unix/macOS:**

```bash
# Gemini API Configuration
export GEMINI_API_KEY='your-gemini-api-key'
export GEMINI_MODEL='gemini-1.5-flash'

# OpenAI Compatible API Configuration (optional)
export OPENAI_COMPATIBLE_API_KEY='your-openai-compatible-api-key'
export OPENAI_COMPATIBLE_BASE_URL='https://your-api-endpoint.com/v1'
export OPENAI_COMPATIBLE_MODEL='your-model-name'
```

**Windows PowerShell:**

```powershell
# Gemini API Configuration
$env:GEMINI_API_KEY='your-gemini-api-key'
$env:GEMINI_MODEL='gemini-1.5-flash'

# OpenAI Compatible API Configuration (optional)
$env:OPENAI_COMPATIBLE_API_KEY='your-openai-compatible-api-key'
$env:OPENAI_COMPATIBLE_BASE_URL='https://your-api-endpoint.com/v1'
$env:OPENAI_COMPATIBLE_MODEL='your-model-name'
```

## 🚀 Usage Guide

⚠️ **Note**: The backtesting system is currently under testing.

The system supports multiple running modes:

### 1. Command Line Analysis Mode

This is the main way to interact directly with the system for stock analysis.

**Basic Run (only shows key decision information):**

```bash
poetry run python src/main.py --ticker 000000 #change to the stock code you want to test
```

For example, to analyze stock code `301155`:

```bash
poetry run python src/main.py --ticker 301155
```

**Show Detailed Reasoning Process (view the analysis process of each agent):**

```bash
poetry run python src/main.py --ticker 000000 --show-reasoning #change to the stock code you want to test
```

For example:

```bash
poetry run python src/main.py --ticker 301155 --show-reasoning
```

**Backtesting Function**
```bash
poetry run python src/backtester.py --ticker 301157 --start-date 2024-12-11 --end-date 2025-01-07 --num-of-news 20
```

The backtesting function supports the following parameters:

- `ticker`: Stock code  
- `start-date`: Backtesting start date (`YYYY-MM-DD`)  
- `end-date`: Backtesting end date (`YYYY-MM-DD`)  
- `initial-capital`: Initial capital (optional, default is `100,000`)  
- `num-of-news`: Number of news used for sentiment analysis (optional, default is `5`, maximum is `100`)  

#### Parameter Description
- `--ticker`: Stock code (required)  
- `--show-reasoning`: Show analysis reasoning process (optional, default is `false`)  
- `--initial-capital`: Initial cash amount (optional, default is `100,000`)  
- `--num-of-news`: Number of news used for sentiment analysis (optional, default is `5`, maximum is `100`)  
- `--start-date`: Start date, format `YYYY-MM-DD` (optional)  
- `--end-date`: End date, format `YYYY-MM-DD` (optional) 


### 2. Backend API Service Mode

This mode starts a FastAPI backend service, allowing interaction with the system via API, suitable for users who want to develop custom frontend interfaces based on this backend.

```bash
# Start API service
poetry run python run_with_backend.py
```

After starting, you can access the interactive API interface (Swagger UI) by visiting `http://localhost:8000/docs` in your browser.

**Common API endpoints include:**

- **Start a new analysis**: `POST /analysis/start` (provide stock code, initial capital, etc. in the request body)
- **View current workflow status**: `GET /api/workflow/status` (get current run ID and active Agent status)
- **List historical runs**: `GET /runs/` (get list of completed runs)
- **View flow chart for a specific run**: `GET /runs/{run_id}/flow`
- **View detailed execution log for a specific Agent**: `GET /runs/{run_id}/agents/{agent_name}`
- **View LLM interaction logs**: `GET /logs/` (specific path may need to be confirmed based on implementation)

**Advantages of API Service Mode:**

- Analysis tasks execute asynchronously in the background.
- All results are queryable via API.
- No need to restart the program for each analysis.
- Can serve as a foundation for developing custom frontends.

For detailed backend API documentation, please refer to: [View Detailed Backend API Documentation](./backend/README.md)

### Parameter Description (Command Line Mode)

- `--ticker`: Stock code (required)
- `--show-reasoning`: Show analysis reasoning process (optional, default is `false`)
- `--initial-capital`: Initial cash amount (optional, default is `100,000`)
- `--num-of-news`: Number of news used for sentiment analysis (optional, default is `5`)

### Command Line Mode Output Description

The system will output the following information:

1. Fundamental analysis results
2. Valuation analysis results
3. Technical analysis results
4. Sentiment analysis results
5. Risk management assessment
6. Final trading decision

If the `--show-reasoning` parameter is used, the detailed analysis process of each agent will also be displayed.

**Example Output:**

```
Retrieving historical market data for 301157...
Start date: 2024-12-11
End date: 2024-12-11
Successfully retrieved historical market data, 242 records in total

Warning: The following indicators have NaN values:
- momentum_1m: 20 items
- momentum_3m: 60 items
- momentum_6m: 120 items
...(these warnings are normal, due to some technical indicators requiring longer historical data to calculate)

Retrieving financial indicator data for 301157...
Getting real-time quotes...
Successfully retrieved real-time quote data

Getting Sina financial indicators...
Successfully retrieved Sina financial indicator data, 3 records in total
Latest data date: 2024-09-30 00:00:00

Getting income statement data...
Successfully retrieved income statement data

Building indicator data...
Successfully built indicator data

Final Result:
{
  "action": "buy",
  "quantity": 12500,
  "confidence": 0.42,
  "agent_signals": [
    {
      "agent": "Technical Analysis",
      "signal": "bullish",
      "confidence": 0.6
    },
    {
      "agent": "Fundamental Analysis",
      "signal": "neutral",
      "confidence": 0.5
    },
    {
      "agent": "Sentiment Analysis",
      "signal": "neutral",
      "confidence": 0.8
    },
    {
      "agent": "Valuation Analysis",
      "signal": "bearish",
      "confidence": 0.99
    },
    {
      "agent": "Risk Management",
      "signal": "buy",
      "confidence": 1.0
    }
  ],
  "reasoning": "Risk Management allows a buy action with a maximum quantity of 12500..."
}
```

### Log File Description

The system will generate the following types of log files in the `logs/` directory:

1. **Backtest Logs**

   - File name format: `backtest_{stock_code}_{current_date}_{backtest_start_date}_{backtest_end_date}.log`
   - Example: `backtest_301157_20250107_20241201_20241230.log`
   - Contains: Analysis results, trading decisions, and portfolio status for each trading day

2. **API Call Logs**
   - File name format: `api_calls_{current_date}.log`
   - Example: `api_calls_20250107.log`
   - Contains: Detailed information and responses for all API calls

All date formats are YYYY-MM-DD. If the `--show-reasoning` parameter is used, the detailed analysis process will also be recorded in the log files.

## 📂 Project Structure

```
trading_agent/
├── backend/                     # Backend API and services
│   ├── dependencies.py          # Dependency injection (e.g., LogStorage)
│   ├── main.py                  # FastAPI application instance
│   ├── models/                  # API request/response models (Pydantic)
│   │   ├── analysis.py          # /analysis/ related routes
│   │   ├── api_runs.py          # /api/runs/ related routes (based on api_state)
│   │   ├── logs.py              # /logs/ related routes
│   │   ├── runs.py              # /runs/ related routes (based on BaseLogStorage)
│   │   └── workflow.py          # /api/workflow/ related routes
│   ├── schemas.py               # Internal data structures/log models (Pydantic)
│   ├── services/                # Business logic services
│   │   └── analysis.py          # Stock analysis service
│   ├── state.py                 # In-memory state management (api_state)
│   ├── storage/                 # Log storage implementation
│   │   ├── base.py              # BaseLogStorage interface definition
│   │   └── memory.py            # InMemoryLogStorage implementation
│   └── utils/                   # Backend utility functions
│       ├── api_utils.py         # API-related tools
│       └── context_managers.py  # Context managers (e.g., workflow_run)
├── src/                         # Agent core logic and tools
│   ├── agents/                  # Agent definitions and workflows
│   │   ├── __init__.py
│   │   ├── debate_room.py
│   │   ├── fundamentals.py
│   │   ├── macro_analyst.py       # Macro Analyst Agent
│   │   ├── market_data.py
│   │   ├── portfolio_manager.py
│   │   ├── researcher_bear.py
│   │   ├── researcher_bull.py
│   │   ├── risk_manager.py
│   │   ├── sentiment.py
│   │   ├── state.py
│   │   ├── technicals.py
│   │   └── valuation.py
│   ├── data/                   # Data storage directory (local cache, etc.)
│   │   ├── img/                # Project images
│   │   ├── sentiment_cache.json  # Sentiment analysis result cache
│   │   ├── macro_analysis_cache.json  # Macro analysis result cache
│   │   └── stock_news/         # Stock news data
│   ├── tools/                  # Tools and function modules (LLM, data acquisition)
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── data_analyzer.py
│   │   ├── news_crawler.py
│   │   └── openrouter_config.py
│   ├── utils/                  # Common utility functions (logs, LLM clients, serialization)
│   │   ├── __init__.py
│   │   ├── api_utils.py        # Agent shared API tools (gradually migrating to backend)
│   │   ├── llm_clients.py
│   │   ├── llm_interaction_logger.py
│   │   ├── logging_config.py
│   │   ├── output_logger.py
│   │   ├── serialization.py
│   │   ├── structured_terminal.py  # Structured terminal output
│   │   └── summary_report.py    # Summary report generation
│   ├── backtester.py          # Backtesting system (may need status check)
│   └── main.py                # Agent workflow definition and command line entry
├── logs/                      # Log file directory (mainly generated by OutputLogger)
├── .env                       # Environment variable configuration
├── .env.example              # Environment variable example
├── poetry.lock               # Poetry dependency lock file
├── pyproject.toml            # Poetry project configuration
├── run_with_backend.py       # Script to start backend and optionally execute analysis
└── README.md                 # Project documentation
```

## 📖 Project Detailed Description

### Architecture Design

This project is an AI investment system based on multiple agents, adopting a modular design where each agent has its dedicated responsibilities. The system architecture is as follows:

```
Market Data Analyst → [Technical/Fundamentals/Sentiment/Valuation Analyst & Researcher Bull/Bear & Debate Room] → Risk Manager → Portfolio Manager → Trading Decision
```

#### Agent Roles and Responsibilities

1. **Market Data Analyst**

   - Serves as the entry point of the system
   - Responsible for collecting and preprocessing all necessary market data
   - Obtains A-share market data through the akshare API
   - Data sources: East Money, Sina Finance, etc.

2. **Technical Analyst**

   - Analyzes price trends, volume, momentum, and other technical indicators
   - Generates trading signals based on technical analysis
   - Focuses on short-term market trends and trading opportunities

3. **Fundamentals Analyst**

   - Analyzes company financial indicators and operational status
   - Evaluates the company's long-term development potential
   - Generates trading signals based on fundamentals

4. **Sentiment Analyst**

   - Analyzes market news and public opinion data
   - Evaluates market sentiment and investor behavior
   - Generates trading signals based on sentiment

5. **Valuation Analyst**

   - Conducts company valuation analysis
   - Assesses the intrinsic value of stocks
   - Generates trading signals based on valuation

6. **Researcher Bull / Researcher Bear** (New)

   - Conducts in-depth research and analysis from bullish and bearish perspectives respectively, providing opposing viewpoints.

7. **Debate Room** (New and Enhanced)

   - Bull and bear researchers present their views and engage in debate.
   - Introduces LLM as a third-party analyst to objectively evaluate debate content and viewpoints.
   - Integrates various perspectives and LLM scores to form a more comprehensive decision basis.

8. **Risk Manager**

   - Integrates trading signals from all agents and debate results
   - Assesses potential risks
   - Sets trading limits and risk control parameters
   - Generates risk management signals

9. **Portfolio Manager**
   - Acts as the final decision maker
   - Comprehensively considers all signals, debate results, and risk factors
   - Makes the final trading decision (buy/sell/hold)
   - Ensures decisions comply with risk management requirements

### Data Flow and Processing

#### Data Types

1. **Market Data**

   ```python
   {
      "market_cap": float,        # Total market capitalization
      "volume": float,            # Trading volume
      "average_volume": float,    # Average volume
      "fifty_two_week_high": float,  # 52-week high
      "fifty_two_week_low": float    # 52-week low
   }
   ```

2. **Financial Metrics**

   ```python
   {
      # Market data
      "market_cap": float,          # Total market capitalization
      "float_market_cap": float,    # Float market capitalization

      # Profitability data
      "revenue": float,             # Total operating revenue
      "net_income": float,          # Net profit
      "return_on_equity": float,    # Return on equity
      "net_margin": float,          # Net profit margin
      "operating_margin": float,    # Operating profit margin

      # Growth indicators
      "revenue_growth": float,      # Main business revenue growth rate
      "earnings_growth": float,     # Net profit growth rate
      "book_value_growth": float,   # Net asset growth rate

      # Financial health indicators
      "current_ratio": float,       # Current ratio
      "debt_to_equity": float,      # Debt-to-equity ratio
      "free_cash_flow_per_share": float,  # Free cash flow per share
      "earnings_per_share": float,  # Earnings per share

      # Valuation ratios
      "pe_ratio": float,           # Price-to-earnings ratio (dynamic)
      "price_to_book": float,      # Price-to-book ratio
      "price_to_sales": float      # Price-to-sales ratio
   }
   ```

3. **Financial Statements**

   ```python
   {
      "net_income": float,          # Net profit
      "operating_revenue": float,    # Total operating revenue
      "operating_profit": float,     # Operating profit
      "working_capital": float,      # Working capital
      "depreciation_and_amortization": float,  # Depreciation and amortization
      "capital_expenditure": float,  # Capital expenditure
      "free_cash_flow": float       # Free cash flow
   }
   ```

4. **Trading Signals**
   ```python
   {
      "action": str,               # "buy", "sell", "hold"
      "quantity": int,             # Trading quantity
      "confidence": float,         # Confidence (0-1) (may be hybrid confidence)
      "agent_signals": [           # Signals from each agent
          {
              "agent": str,        # Agent name
              "signal": str,       # "bullish", "bearish", "neutral"
              "confidence": float  # Confidence (0-1)
          }
      ],
      "reasoning": str            # Decision rationale (may include debate summary and LLM assessment)
   }
   ```

#### Data Flow Process

1. **Data Collection Stage**

   - Market Data Agent obtains real-time market data through akshare API:
     - Stock real-time quotes (`stock_zh_a_spot_em`)
     - Historical market data (`stock_zh_a_hist`)
     - Financial indicator data (`stock_financial_analysis_indicator`)
     - Financial statement data (`stock_financial_report_sina`)
   - News data is obtained through Sina Finance API
   - All data undergoes standardization processing and formatting

2. **Analysis Stage**

   - Technical Analyst: Calculates technical indicators, analyzes price patterns, generates technical analysis scores and recommendations.
   - Fundamentals Analyst: Analyzes financial statements, evaluates fundamentals, generates fundamental analysis scores.
   - Sentiment Analyst: Analyzes market news, uses AI models to evaluate sentiment, generates market sentiment scores.
   - Valuation Analyst: Calculates valuation indicators, performs DCF valuation, assesses intrinsic value.
   - Researcher Bull/Bear: Conducts in-depth analysis from their respective standpoints, prepares debate materials.

3. **Debate and Evaluation Stage (Debate Room)**

   - Bull and bear researchers submit their viewpoints.
   - The system summarizes viewpoints, potentially assisted by LLM to generate structured analysis.
   - LLM acts as a third party to objectively evaluate viewpoints and provide scores.
   - Calculates hybrid confidence.

4. **Risk Assessment Stage**
   Risk Manager comprehensively considers multiple dimensions:

   - Market risk assessment (volatility, Beta, etc.)
   - Position size limit calculation
   - Stop-loss and take-profit level setting
   - Portfolio risk control
   - Integration of enhanced signals from the debate room.

5. **Decision Stage**
   Portfolio Manager makes decisions based on the following factors:

   - Signal strength and confidence from each Agent.
   - Comprehensive conclusions and hybrid confidence from the debate room.
   - Current market conditions and risk levels.
   - Portfolio status and cash levels.
   - Trading costs and liquidity considerations.

6. **Data Storage and Caching**

   - Sentiment analysis results are cached in `data/sentiment_cache.json`
   - News data is saved in the `data/stock_news/` directory
   - Log files are stored by type in the `logs/` directory
   - API call records are written to logs in real-time

7. **Monitoring and Feedback**
   - All API calls have detailed log records
   - The analysis process of each Agent can be tracked
   - System decision process (including debate phase) is transparent and queryable
   - Backtesting results provide performance evaluation

### Agent Collaboration Mechanism

1. **Information Sharing**

   - All agents share the same state object (AgentState) or pass information through clearly defined data structures.
   - Communication occurs through message passing mechanisms or sequential calls.
   - Each agent can access necessary historical data and preceding analysis results.

2. **Decision Weighting and Fusion**
   Portfolio Manager considers the weights of different signals when making decisions, combined with the hybrid confidence from the debate room:

   - Valuation analysis: (example weight) 35%
   - Fundamental analysis: (example weight) 30%
   - Technical analysis: (example weight) 25%
   - Sentiment analysis: (example weight) 10%
   - Debate room conclusion: May serve as an important adjustment factor or independent confidence source for the final decision.

3. **Risk Control**
   - Mandatory risk limits
   - Maximum position limits
   - Trading size limits
   - Stop-loss and take-profit settings

### System Features

1. **Multi-LLM Support**

   - Supports Google Gemini API
   - Supports any LLM service compatible with OpenAI API format (such as Huawei Cloud Pangu, OpenRouter, etc.)
   - Smart switching function: Automatically selects available LLM services

2. **Modular Design**

   - Each agent is an independent module
   - Easy to maintain and upgrade
   - Can be tested and optimized individually

3. **Scalability**

   - Can easily add new analyst or researcher roles
   - Supports adding new data sources
   - Can expand decision strategies and debate mechanisms

4. **Risk Management**

   - Multi-level risk control
   - Real-time risk assessment
   - Automatic stop-loss mechanism (planned or partially implemented)

5. **Intelligent Decision-Making and Explainability**
   - Based on multi-dimensional analysis and multi-party viewpoint game theory
   - Considers multiple market factors
   - Dynamically adjusts strategies
   - Enhances transparency and explainability of the decision process through `--show-reasoning` and debate room mechanisms

### Future Outlook

1. **Data Source Expansion**

   - Add more A-share data sources (such as structured data for financial reports and announcements)
   - Connect to more financial data platforms
   - Add alternative data such as social media sentiment data and industry research reports
   - Expand to Hong Kong and US stock markets

2. **Feature Enhancement**

   - Add more complex technical indicators and quantitative strategy factors
   - Implement a more complete and automated backtesting system, supporting parameter optimization
   - Support multi-stock portfolio management and dynamic position adjustment
   - Enhance LLM application in strategy generation, code explanation, market summaries, etc.

3. **Performance Optimization**
   - Improve data processing efficiency, optimize inter-Agent communication
   - Optimize decision algorithms and LLM call efficiency
   - Increase parallel processing capability, supporting larger-scale analysis tasks

### Sentiment Analysis Feature (Sentiment Agent)

The Sentiment Agent is one of the key components in the system, responsible for analyzing the potential impact of market news and public opinion on stocks.

#### Feature Characteristics

1. **News Data Collection**

   - Automatically scrapes the latest stock-related news
   - Supports multiple news sources (currently mainly Sina Finance)
   - Updates news data in real-time (based on call frequency)

2. **Sentiment Analysis Processing**

   - Uses advanced AI models (LLM) to analyze news sentiment
   - Sentiment score range: -1 (extremely negative) to 1 (extremely positive)
   - Considers the importance and timeliness of news (implicit or explicit)

3. **Trading Signal Generation**
   - Generates trading signals based on sentiment analysis results
   - Includes signal type (bullish/bearish/neutral)
   - Provides confidence assessment
   - Includes detailed analysis rationale (possibly summarized by LLM)

#### Sentiment Score Description

- **1.0**: Extremely positive (major positive news, better-than-expected performance, supportive industry policies)
- **0.5 to 0.9**: Positive (performance growth, new project implementation, order acquisition)
- **0.1 to 0.4**: Slightly positive (small contract signing, normal daily operations)
- **0.0**: Neutral (routine announcements, personnel changes, news with no significant impact)
- **-0.1 to -0.4**: Slightly negative (small litigation, non-core business losses)
- **-0.5 to -0.9**: Negative (performance decline, loss of important customers, tightening industry policies)
- **-1.0**: Extremely negative (major violations, serious losses in core business, regulatory penalties)

## 🙏 Acknowledgements

This project is modified from [ai-hedge-fund](https://github.com/virattt/ai-hedge-fund.git). 