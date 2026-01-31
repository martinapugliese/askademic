# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Askademic is a CLI tool that helps users find information in research papers from arXiv. It's built on PydanticAI and provides:
- Summarization of latest papers in categories
- Question answering by searching relevant papers
- Specific paper retrieval by title/link/arXiv ID

## Development Commands

### Installation & Setup
```bash
pip install .                    # Install the package
pip install -e .                 # Install in development mode
```

### Testing
```bash
pytest                          # Run all tests
pytest tests/test_article.py    # Run specific test file
python evals/evals.py           # Run evaluation tests
```

### Running the Application
```bash
askademic                       # Start the CLI application
```

### Code Quality
```bash
flake8                          # Lint code (max line length: 99)
pre-commit run --all-files      # Run pre-commit hooks
```

## Architecture

### Core Components

1. **main.py**: Entry point with CLI interface using prompt_toolkit and rich console
2. **orchestrator.py**: Main coordination agent that routes requests to specialized agents
3. **allower.py**: Determines if user queries are scientific (routes to orchestrator or returns puns)
4. **Specialized Agents**:
   - **summary.py**: SummaryAgent for latest paper summaries
   - **question.py**: QuestionAgent for Q&A with arXiv search
   - **article.py**: ArticleAgent for specific paper retrieval and analysis
5. **memory.py**: Manages conversation context and token limits
6. **utils.py**: Model selection and arXiv API utilities
7. **tools.py**: Utility functions for arXiv interactions

### Agent Architecture
- Built on PydanticAI with structured Pydantic model outputs
- Uses orchestrator pattern - main orchestrator routes to specialized agents
- Each agent has specific tools and capabilities
- Memory management tracks conversation history with token limits

### Model Support
- **Gemini 2.0 Flash** (default, preferred for cost and context window)
- **Claude 4.5 Haiku** (experimental, rate limited)
- **Claude via AWS Bedrock** (experimental)

## Configuration

### Environment Variables
Required in `.env` file (copy from `.env-template`):
- `LLM_FAMILY`: "gemini", "claude", or "claude-aws-bedrock"
- `GOOGLE_API_KEY`: For Gemini models
- `ANTHROPIC_API_KEY`: For Claude models
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`: For AWS Bedrock

### Key Settings
- Max request tokens: 100,000 (configured in memory.py)
- Usage limits: 20 requests per agent run
- Default temperature: 0 for consistency
- Retry strategy: 20 retries with early termination

## Development Guidelines

### File Structure
- `src/askademic/`: Main package
- `prompts/`: System prompts in separate files
- `tests/`: Unit tests for each component
- `evals/`: Evaluation scripts
- `logs/`: Daily log files (auto-generated)

### Testing Strategy
- Unit tests for each agent and utility
- Manual evaluation suite in `evals/` directory
- CI/CD with GitHub Actions testing Python 3.11-3.13

### Agent Development
- Each agent follows PydanticAI patterns with structured outputs
- Tools decorated with `@agent.tool` for function calling
- Async/await throughout for API calls
- Comprehensive logging to daily log files

### Memory Management
- Conversation history maintained with token counting
- Automatic cleanup when limits exceeded
- Context window management for different models
