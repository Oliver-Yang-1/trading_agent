# SuperAgent

A LangGraph-based agent workflow system for intelligent task automation.

## Features

- Multi-agent orchestration with LangGraph
- Web crawling and content extraction
- FastAPI backend with SSE streaming
- Browser automation capabilities
- Configurable LLM integration

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

## Configuration

Create a `.env` file in the project root with your API keys and configuration.