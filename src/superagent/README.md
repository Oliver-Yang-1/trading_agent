# SuperAgent

A LangGraph-based agent workflow system for intelligent task automation.

## Features

- Multi-agent orchestration with LangGraph
- Web crawling and content extraction
- FastAPI backend with SSE streaming
- Browser automation capabilities
- Configurable LLM integration
- Automated report generation with markdown output
- Algogene integration for data archiving and model generation

## Installation

```bash
poetry install
```

## Usage

### Running the API server

```bash
poetry run python server.py
```

### Running the main application

```bash
poetry run python main.py
```

## Development

### Installing development dependencies

```bash
poetry install --with dev,test
```

### Running tests

```bash
poetry run pytest
```

### Code formatting

```bash
poetry run black .
```

## Output Directories

### Reporter Output
The reporter agent automatically generates comprehensive markdown reports that are saved to:
```
./reports/
```
Reports are named with timestamps (e.g., `report_20250718_101610.md`) and contain:
- Executive summary
- Key findings
- Detailed analysis
- Conclusions and recommendations

### Algogene Archive Output
The algogene_archieve agent generates trading strategies and models that are saved to:
```
./generated_models/strategies/
```
This directory contains:
- **Strategy folders**: `arbitrage/`, `custom/`, `market_making/`, `mean_reversion/`, `trend_following/`
- **Generated files**: Python strategy files with timestamps and corresponding README documentation
- **Examples**: 
  - `sol_moving_average_hourly_20250718_101502.py` - Generated trading strategy
  - `sol_moving_average_hourly_README.md` - Strategy documentation

## Configuration

Create a `.env` file in the project root with your API keys and configuration.