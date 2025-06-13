# Auto-Codex Examples

This directory contains **comprehensive examples** demonstrating how to use the auto_codex library for various AI coding tasks. Each example showcases specific features with clean, production-ready code.

## Available Examples

### 1. Basic Usage (`basic_usage_example.py`)

**Core auto_codex functionality:**
- Single run creation and execution
- Session management with multiple runs
- Result extraction and processing

```python
from auto_codex import CodexRun, CodexSession

# Single run
run = CodexRun(prompt="Create a Python function", model="gpt-4", provider="openai")

# Session with multiple runs
session = CodexSession(session_id="demo-session")
run = session.add_run(prompt="Build a web scraper", model="gpt-4", provider="openai")
```

**Perfect for:** Getting started, understanding core concepts

### 2. Health Monitoring (`health_monitoring_example.py`)

**Agent health monitoring and analytics:**
- Basic health status checking
- Real-time monitoring with alerts
- Session health monitoring
- Health analytics and reporting

```python
from auto_codex import CodexRun, get_health_monitor

run = CodexRun(prompt="Process data", model="gpt-4", provider="openai", enable_health_monitoring=True)
health = run.get_health_status()
print(f"Status: {health.status.value}, Health: {health.health.value}")
```

**Perfect for:** Production deployments, monitoring AI agents

### 3. Interactive Controller (`interactive_controller_example.py`)

**Advanced agent control and management:**
- Starting and stopping agents
- Callback-driven workflows
- Dynamic agent management
- Agent status monitoring

```python
from auto_codex import CodexSession

class SimpleAgentController:
    def start_agent(self, task: str) -> CodexRun:
        # Agent control logic
        pass
```

**Perfect for:** Sophisticated agent management, automation systems

### 4. Real-Time Inspector (`real_time_inspector_example.py`)

**Live agent inspection and monitoring:**
- Real-time status monitoring
- Detailed agent inspection
- Event logging and history
- Monitoring dashboards

```python
from auto_codex import get_health_monitor

class SimpleAgentInspector:
    def start_monitoring(self, runs: List[CodexRun]):
        # Real-time monitoring logic
        pass
```

**Perfect for:** Production monitoring, debugging, dashboards

### 5. Interactive Usage (`interactive_usage_example.py`)

**Interactive session management:**
- Dynamic task addition
- Real-time progress monitoring
- Result processing and extraction
- Session coordination

```python
from auto_codex import CodexSession

class InteractiveCodexDemo:
    def add_task(self, prompt: str) -> CodexRun:
        # Interactive task management
        pass
```

**Perfect for:** Interactive workflows, dynamic task management

### 6. Log Parsing & Data Extraction (`log_parsing_example.py`)

**Parse and analyze Codex logs:**
- Log file parsing with `CodexLogParser`
- Data extraction with `PatchExtractor`, `CommandExtractor`, `ToolUsageExtractor`
- Change detection and analysis
- Output parsing and code block extraction
- Batch log analysis

```python
from auto_codex import CodexLogParser, PatchExtractor, CommandExtractor

parser = CodexLogParser(log_dir="./logs")
parsed_runs = parser.parse_all_logs()

extractor = PatchExtractor()
patches = extractor.extract_from_file(log_file)
```

**Perfect for:** Log analysis, data extraction, change tracking

### 7. Provider Support (`provider_examples.py`)

**Multiple AI provider integration:**
- OpenAI, Azure, Gemini, Ollama, Mistral, DeepSeek, xAI, Groq, Arcee AI
- Provider configuration and validation
- Multi-provider sessions
- Provider comparison workflows

```python
from auto_codex import CodexRun, SUPPORTED_PROVIDERS, validate_provider_config

# Different providers
openai_run = CodexRun(prompt="Task 1", model="gpt-4", provider="openai")
gemini_run = CodexRun(prompt="Task 2", model="gemini-pro", provider="gemini")
ollama_run = CodexRun(prompt="Task 3", model="llama2", provider="ollama")
```

**Perfect for:** Multi-provider setups, provider comparison, local models

### 8. Utilities (`utilities_example.py`)

**Template processing, file management, and diff utilities:**
- `TemplateProcessor` for dynamic prompt generation
- `FileManager` for file operations and CSV handling
- `DiffUtils` for code diff analysis
- Batch processing with templates

```python
from auto_codex import TemplateProcessor, FileManager, DiffUtils

# Template processing
processor = TemplateProcessor()
prompt = processor.process_template(template, variables)

# File management
file_manager = FileManager()
content = file_manager.read_file("script.py")

# Diff analysis
diff_lines = DiffUtils.generate_diff(old_code, new_code)
```

**Perfect for:** Template-based workflows, file operations, code analysis

## Quick Start Guide

### 1. Basic Usage
```python
from auto_codex import CodexRun

run = CodexRun(
    prompt="Create a Python function to calculate fibonacci numbers",
    model="gpt-4",
    provider="openai"
)

result = run.execute()
print(f"Success: {result.success}")
```

### 2. With Health Monitoring
```python
from auto_codex import CodexRun

run = CodexRun(
    prompt="Build a web scraper",
    model="gpt-4", 
    provider="openai",
    enable_health_monitoring=True
)

health = run.get_health_status()
print(f"Status: {health.status.value}, Health: {health.health.value}")
```

### 3. Session Management
```python
from auto_codex import CodexSession

session = CodexSession(session_id="my-project")
run1 = session.add_run(prompt="Step 1: Create database schema")
run2 = session.add_run(prompt="Step 2: Build REST API")
run3 = session.add_run(prompt="Step 3: Add authentication")

results = session.execute_all()
```

### 4. Multiple Providers
```python
from auto_codex import CodexSession

session = CodexSession(session_id="multi-provider")
session.add_run(prompt="Create API", model="gpt-4", provider="openai")
session.add_run(prompt="Write docs", model="gemini-pro", provider="gemini")
session.add_run(prompt="Add tests", model="llama2", provider="ollama")
```

## Feature Coverage

| Example | Core | Health | Control | Inspection | Logs | Providers | Utils |
|---------|------|--------|---------|------------|------|-----------|-------|
| basic_usage_example.py | ✅ | | | | | | |
| health_monitoring_example.py | ✅ | ✅ | | | | | |
| interactive_controller_example.py | ✅ | | ✅ | | | | |
| real_time_inspector_example.py | ✅ | ✅ | | ✅ | | | |
| interactive_usage_example.py | ✅ | ✅ | ✅ | | | | |
| log_parsing_example.py | ✅ | | | | ✅ | | |
| provider_examples.py | ✅ | | | | | ✅ | |
| utilities_example.py | ✅ | | | | | | ✅ |

## Running Examples

All examples can be run directly from the examples directory:

```bash
cd auto_codex/examples

# Core functionality
python basic_usage_example.py

# Health monitoring
python health_monitoring_example.py

# Agent control
python interactive_controller_example.py

# Real-time monitoring
python real_time_inspector_example.py

# Interactive usage
python interactive_usage_example.py

# Log parsing
python log_parsing_example.py

# Provider support
python provider_examples.py

# Utilities
python utilities_example.py
```

## Requirements

- Python 3.7+
- auto_codex library installed
- API keys configured for desired providers:
  - `OPENAI_API_KEY` for OpenAI
  - `GEMINI_API_KEY` for Gemini
  - `OLLAMA_API_KEY` for Ollama (if authentication required)
  - See `provider_examples.py` for complete list

## Example Structure

Each example follows a consistent structure:
- **Clean, compact code** - Production-ready implementations
- **Feature demonstrations** - Showcase specific capabilities
- **Error handling** - Robust error management
- **Documentation** - Clear docstrings and comments
- **Modular design** - Reusable components

## Integration Examples

### With Benchmarks
```python
from auto_codex.benchmarks import EasyBenchmark
from auto_codex.examples.health_monitoring_example import basic_health_check

# Run benchmarks with health monitoring
benchmark = EasyBenchmark()
# ... integrate health monitoring
```

### With Custom Workflows
```python
from auto_codex.examples.utilities_example import template_processing_example
from auto_codex.examples.provider_examples import multi_provider_session

# Combine template processing with multi-provider execution
# ... custom workflow implementation
```

## Contributing

When adding new examples:
1. Follow the `*_example.py` naming convention
2. Include comprehensive docstrings
3. Demonstrate specific feature sets
4. Add error handling and validation
5. Update this README with the new example
6. Ensure examples are self-contained

## License

These examples are part of the auto_codex package and follow the same licensing terms. 