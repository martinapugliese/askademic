# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Askademic is an AI agent CLI tool that helps users find information in arXiv research papers. It can:

1. Summarize the latest papers in an arXiv category
2. Answer questions by searching for relevant papers
3. Retrieve information about specific papers by title or URL
4. Handle follow-up questions in conversation

The tool is built using PydanticAI and supports multiple LLM providers:
- Gemini (default, preferred)
- Claude via Anthropic API (experimental)
- Claude via AWS Bedrock (experimental)
- AWS Nova Pro (experimental)

## Commands

### Installation and Setup

```bash
# Install from local repo
pip install .

# Alternative using uv with specific Python version
uv tool install --python python3.11 .

# Environment setup
# Copy .env-template to .env and configure API keys
```

### Development Commands

```bash
# Run tests
pytest

# Run specific test file
pytest tests/test_article.py

# Run linting and formatting (via pre-commit)
pre-commit run --all-files

# Run evaluation suite (from evals folder)
cd evals
python evals.py
```

## Architecture

The codebase follows an agent-based architecture using PydanticAI:

1. **Main Entry Point**: `main.py` - Contains the CLI interface, environment setup, and conversation loop

2. **Core Agents**:
   - `orchestrator.py` - Central agent that routes requests to specialized sub-agents
   - `allower.py` - Determines if queries are scientific/academic and should be answered
   - `article.py` - Handles retrieving and analyzing specific papers
   - `question.py` - Searches for and answers research questions
   - `summary.py` - Creates summaries of latest papers in categories

3. **Supporting Components**:
   - `tools.py` - Functions for interacting with arXiv API
   - `memory.py` - Manages conversation history and token usage
   - `utils.py` - Utility functions for model selection and data processing

4. **Prompt Templates**:
   - `prompts/general.py` - System prompts for the various agents

## Development Guidelines

1. Always run tests with pytest to ensure functionality is maintained

2. Run the eval suite before submitting PRs:
   ```
   python evals.py
   ```

3. Maintain support for multiple LLM providers (Gemini, Claude, AWS)

4. When adding new features, ensure they work with the conversation memory system

5. Follow the existing agent architecture for extending functionality

6. Use pre-commit hooks for consistent code formatting with Black, Flake8, and isort