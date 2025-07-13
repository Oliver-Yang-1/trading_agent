# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered trading agent system that uses multiple specialized agents to analyze stocks and make trading decisions. The system is built with Python using LangGraph for agent orchestration, FastAPI for the backend API, and React for the frontend interface.

## Development Environment Setup

### Python Backend
- Uses Poetry for dependency management
- Requires Python 3.11+
- Install dependencies: `poetry install`
- Activate environment: `poetry shell`

### Frontend
- Located in `frontend/` directory
- React TypeScript application with Tailwind CSS
- Install dependencies: `npm install` (in frontend directory)
- Start development server: `npm start`
- Build for production: `npm run build`

## Key Commands

### Running the System

**Command Line Mode (Primary)**:
```bash
# Basic analysis
poetry run python src/main.py --ticker STOCK_CODE

# With detailed reasoning
poetry run python src/main.py --ticker STOCK_CODE --show-reasoning

# Backtesting
poetry run python src/backtester.py --ticker STOCK_CODE --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```

**API Service Mode**:
```bash
# Start FastAPI backend (includes both CLI and API functionality)
poetry run python run_with_backend.py
```

### Development Tools

**Python Linting and Formatting**:
```bash
# Black formatting
poetry run black src/ backend/

# Import sorting
poetry run isort src/ backend/

# Linting
poetry run flake8 src/ backend/

# Run tests
poetry run pytest
```

**Frontend Development**:
```bash
cd frontend/
npm test
npm run build
```

## Architecture Overview

### Multi-Agent Workflow
The system follows a sophisticated multi-agent architecture orchestrated by LangGraph:

1. **Data Collection**: `market_data_agent` fetches real-time market data via akshare API
2. **Parallel Analysis**: Four agents analyze different aspects:
   - `technical_analyst_agent` - Technical indicators and chart patterns
   - `fundamentals_agent` - Financial statements and metrics
   - `sentiment_agent` - News sentiment analysis
   - `macro_news_agent` - Market-wide news analysis
3. **Research Synthesis**: 
   - `researcher_bull_agent` - Bullish thesis development
   - `researcher_bear_agent` - Bearish thesis development
4. **Debate and Risk Assessment**:
   - `debate_room_agent` - Synthesizes bull/bear perspectives
   - `risk_management_agent` - Assesses risk and position sizing
   - `macro_analyst_agent` - Stock-specific macro context
5. **Final Decision**: `portfolio_management_agent` makes trading decisions

### Project Structure

**Core Agent Code**: `src/agents/`
- `state.py` - Shared state management and workflow utilities
- Individual agent files for each specialized agent
- `super_node.py` - Enhanced agent with ReAct capabilities

**Tools and Utilities**: `src/tools/`
- `algogene_client.py` - Data source integration
- `news_crawler.py` - News fetching
- `code_interpreter.py` - Code execution capabilities
- Test files for individual components

**Backend API**: `backend/`
- FastAPI application with CORS enabled
- Multiple routers: agents, analysis, workflow, logs, runs
- Real-time workflow monitoring and status tracking

**Frontend**: `frontend/`
- React TypeScript SPA
- Tailwind CSS for styling
- Components: InputForm, AnalysisResult

### Key State Management

- **AgentState**: Central state object used across all agents
- **API State**: Backend state tracking for current runs and workflow status
- **Log Storage**: Comprehensive logging of LLM interactions and agent executions

### Data Sources

- **akshare**: Primary Chinese market data source
- **Sina Finance API**: News data
- **Algogene**: Enhanced data source integration (configurable)

## Environment Configuration

The system requires API keys configured in `.env`:
- `GEMINI_API_KEY` - Primary LLM API
- Optional OpenAI-compatible API configuration
- Algogene API configuration for enhanced data

## Testing and Development

- Test files are located in `src/tools/test_*.py`
- No formal test suite is currently configured
- Individual component testing available for news crawler, backtesting, and Gemini integration

## Logging and Monitoring

- Comprehensive logging system in `src/utils/logging_config.py`
- Agent execution tracking in `src/utils/llm_interaction_logger.py`
- Log files stored in `logs/` directory by agent type
- Real-time workflow status available via API endpoints

## Notes for Development

- The system supports both CLI and API modes simultaneously
- Workflow runs are tracked with unique IDs
- Agent reasoning can be displayed for debugging
- Backtesting functionality is available but noted as "under testing"
- The system includes structured terminal output and summary reporting capabilities