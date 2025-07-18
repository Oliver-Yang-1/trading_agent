<div align="center">

# 🤖 AI Trading Agent 🧠

</div>

## Project Overview

This repository contains two complementary AI-powered systems for intelligent automation:

### 1. **AI Trading Agent** (Root Project)
The "Trading Agent System" is designed to develop a sophisticated, AI-driven platform for automated investment analysis and decision-making. In the contemporary financial landscape, the voluminous nature of market data, news, and influencing factors presents a significant challenge for human traders to efficiently process information and make timely, optimal decisions. This project addresses this challenge by creating a system of specialized AI agents that collaborate to analyze various facets of financial markets and individual stocks.
The system aims to emulate the workflow of a human investment analysis team, wherein different experts (e.g., technical analysts, fundamental analysts) contribute their insights, which are subsequently debated and synthesized to formulate a coherent trading strategy. By leveraging technologies such as LangGraph for structured agent workflows and Large Language Models (LLMs) for complex data interpretation (e.g., news sentiment analysis), this project endeavors to provide a robust, data-driven, and potentially automated solution for trading. The ultimate objective is to assist in identifying investment opportunities, managing risk, and executing trades with enhanced precision and efficiency.

### 2. **SuperAgent** (Sub-Project)
SuperAgent is a LangGraph-based multi-agent workflow system for intelligent task automation. It provides a flexible framework for orchestrating AI agents to perform complex tasks including web crawling, content extraction, browser automation, and data analysis. The system features a FastAPI backend with Server-Sent Events (SSE) streaming for real-time workflow monitoring and supports configurable LLM integration for diverse automation scenarios.


## System Architecture

The core of the system is its multi-agent architecture. Based on the latest provided architecture diagram, the process flow is as follows:
![image](https://github.com/user-attachments/assets/f73574d2-a682-472a-947a-a04f1b191e0a)

The workflow is described below: 
- Data Ingestion: Commences with the Market Data Agent.
- Parallel Analysis: Data is disseminated to the Technical Analyst Agent, Fundamentals Agent, Sentiment Agent, and the Macro News Agent (providing market-wide insights).
- Viewpoint Synthesis: The outputs from these four analytical agents are passed to the Researcher Bull Agent and the Researcher Bear Agent.
- Debate and Refinement: The bullish and bearish theses are processed by the Debate Room Agent.
- Risk Assessment & Stock-Specific Macro Context: The outcome of the debate is transmitted to the Risk Management Agent, and subsequently to the stock-specific Macro Analyst Agent.
- Final Decision: The Portfolio Management Agent renders the final trading decision.

### Data Flow and Processing

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
   - Fundamental analysis: (example weight) 30%
   - Technical analysis: (example weight) 25%
   - Sentiment analysis: (example weight) 10%
   - Macro News analysis: (example weight) 35%
   - Debate room conclusion: May serve as an important adjustment factor or independent confidence source for the final decision.

3. **Risk Control**
   - Mandatory risk limits
   - Maximum position limits
   - Trading size limits
   - Stop-loss and take-profit settings

## 🛠️ Installation and Setup

First, clone this repository to your local machine.

### 1. Install Poetry

Poetry is a tool for Python dependency management and packaging.

**macOS:**

```bash
curl -sSL [https://install.python-poetry.org](https://install.python-poetry.org) | python3 -
```

### 2. Install Project Dependencies

#### For AI Trading Agent (Root Project):

```bash
poetry lock --no-update
poetry install
```

#### For SuperAgent (Sub-Project):

```bash
cd src/superagent
poetry install
```

### 3. Configure Environment Variables

#### For AI Trading Agent (Root Project):

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


#### For SuperAgent (Sub-Project):

```bash
cd src/superagent
cp .env.example .env
```

Edit the `.env` file to configure your API keys. The SuperAgent supports multiple LLM providers and requires the following environment variables:

**Required LLM Configuration:**
```env
# Reasoning LLM (for complex reasoning tasks)
REASONING_API_KEY=sk-or-v1-your-openrouter-api-key
REASONING_BASE_URL=https://openrouter.ai/api/v1
REASONING_MODEL=anthropic/claude-sonnet-4

# Non-reasoning LLM (for straightforward tasks)
BASIC_API_KEY=sk-or-v1-your-openrouter-api-key
BASIC_BASE_URL=https://openrouter.ai/api/v1
BASIC_MODEL=anthropic/claude-sonnet-4

# Vision-language LLM (for tasks requiring visual understanding)
VL_API_KEY=sk-or-v1-your-openrouter-api-key
VL_BASE_URL=https://openrouter.ai/api/v1
VL_MODEL=anthropic/claude-sonnet-4
```

**Application Settings:**
```env
# Application Settings
DEBUG=True
APP_ENV=development
```

**Optional Services:**
```env
# Web Search API (for web search capabilities)
TAVILY_API_KEY=tvly-your-tavily-api-key

# Browser automation settings (optional, for Chrome-based automation)
# CHROME_INSTANCE_PATH=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome

# OpenAI Compatible API Configuration (alternative LLM provider)
OPENAI_COMPATIBLE_API_KEY=sk-or-v1-your-openrouter-api-key
OPENAI_COMPATIBLE_BASE_URL=https://openrouter.ai/api/v1
OPENAI_COMPATIBLE_MODEL=google/gemini-2.5-flash

# Algogene API Configuration (for enhanced financial data integration)
ALGOGENE_API_KEY=your-algogene-api-key
ALGOGENE_USER_ID=your-algogene-user-id
```

## 🚀 Usage Guide

### AI Trading Agent (Root Project)

⚠️ **Note**: The backtesting system is currently under testing.

The system supports multiple running modes:

#### 1. Command Line Analysis Mode

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

##### Parameter Description
- `--ticker`: Stock code (required)  
- `--show-reasoning`: Show analysis reasoning process (optional, default is `false`)  
- `--initial-capital`: Initial cash amount (optional, default is `100,000`)  
- `--num-of-news`: Number of news used for sentiment analysis (optional, default is `5`, maximum is `100`)  
- `--start-date`: Start date, format `YYYY-MM-DD` (optional)  
- `--end-date`: End date, format `YYYY-MM-DD` (optional) 

#### 2. Backend API Service Mode

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

### SuperAgent (Sub-Project)

SuperAgent provides a flexible multi-agent workflow system for intelligent task automation.

#### Running SuperAgent

**Command Line Mode**

```bash
cd src/superagent
poetry run python main.py
```

#### SuperAgent Features

- **Multi-agent orchestration**: Coordinate multiple AI agents using LangGraph
- **Web crawling and extraction**: Intelligent content extraction from web pages
- **Browser automation**: Automated web browsing capabilities
- **Data analysis**: Built-in tools for data processing and analysis
- **Flexible LLM integration**: Support for multiple LLM providers

For detailed SuperAgent documentation, please refer to: [SuperAgent README](./src/superagent/README.md)






### Future Outlook

**- Integration with Algogene for More Comprehensive Data**:
  - Objective: To expand data sources, thereby enhancing the breadth and depth of analysis.
  - Potential of Algogene: Access to more detailed market data, richer company announcements and news, and supplementary macroeconomic data.
  - Challenges: API integration, data cleansing, and format unification.
**- Exploration of More Flexible AI Combinations & Strategy Generation:**
  - Objective: To transcend fixed agent interaction flows, enabling more adaptable and intelligent strategy construction.
  - Prospective Ideas:
    - Allowing dynamic agent selection and combination.
    - Implementing LLM-driven recommendations for agent workflows.
    - Utilizing LLMs for the generation of initial trading strategy logic.
  - Value Proposition: Catering to diverse use cases, thereby enhancing system adaptability and intelligence.
**- Interfacing with the Algogene Platform for Strategy Execution & Backtesting:**
  - Objective: To translate AI-driven analysis into executable strategies on the Algogene platform and to validate these strategies.
  - Implementation Pathway:
    - Converting system decisions into Algogene-compatible orders.
    - Employing Algogene trading APIs for execution.
    - Leveraging Algogene for backtesting and live testing.
  - Value Proposition: Creating a closed-loop system from AI analysis to execution and validation.


## 🙏 Acknowledgements

This project is modified from [ai-hedge-fund](https://github.com/virattt/ai-hedge-fund.git). 
