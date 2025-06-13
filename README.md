# Codex Interaction Library

A comprehensive Python library for interacting with Codex, parsing logs, and managing Codex runs. Each run of Codex is represented as its own class with parsing capabilities for outputs.

## Features

- **Individual Codex Runs**: Each Codex execution is represented as a `CodexRun` class with complete lifecycle management
- **Session Management**: Group multiple runs into sessions with `CodexSession` for batch processing
- **Log Parsing**: Comprehensive parsing of Codex log files with multiple extraction types
- **Template Processing**: Jinja2-based template processing for dynamic prompt generation
- **CSV Integration**: Built-in support for processing CSV data with templated prompts
- **File Management**: Utilities for backups, file operations, and directory management
- **Diff Utilities**: Tools for analyzing and displaying file changes
- **Pure Interaction Focus**: Separated from interface code, focused purely on Codex interaction

## Installation

```bash
# Install dependencies
pip install jinja2

# The library is designed to be used as a local module
# Copy the codex_interaction directory to your project
```

## Quick Start

### Basic Usage

```python
from codex_interaction import CodexRun, CodexSession, CodexLogParser

# Create and execute a single Codex run
run = CodexRun(
    prompt="Create a Python function to calculate fibonacci numbers",
    model="gpt-4.1-nano",
    timeout=300
)

result = run.execute(log_dir="./logs")
print(f"Success: {result.success}")
print(f"Files modified: {result.files_modified}")
```

### Session with Multiple Runs

```python
# Create a session for multiple runs
session = CodexSession(
    session_id="my_session",
    default_model="gpt-4.1-nano",
    log_dir="./logs"
)

# Add multiple runs
session.add_run("Create a calculator class")
session.add_run("Write unit tests for the calculator")
session.add_run("Add documentation to the code")

# Execute all runs
session_result = session.execute_all()
summary = session.get_summary()
```

### CSV Data Processing

```python
from codex_interaction import TemplateProcessor

# CSV data
csv_data = [
    {"file_path": "api/users.py", "method": "GET", "endpoint": "/api/users"},
    {"file_path": "api/orders.py", "method": "POST", "endpoint": "/api/orders"}
]

# Template
template = """
Analyze the API endpoint {{ endpoint }} with method {{ method }} in {{ file_path }}.
Check for security and error handling.
"""

# Process with session
session = CodexSession()
processor = TemplateProcessor()
result = session.process_csv_data(csv_data, template, processor)
```

### Log Parsing

```python
# Parse existing Codex logs
parser = CodexLogParser(log_dir=".", log_pattern="codex_run_*.log")

# Parse all logs
results = parser.parse_logs()

# Parse specific run
run_result = parser.parse_run("codex_run_20241201_123456.log")
print(f"Changes: {len(run_result.changes)}")
print(f"Tool usage: {len(run_result.tool_usage)}")
```

## Library Architecture

### Core Classes

- **`CodexRun`**: Represents a single Codex execution with full lifecycle management
- **`CodexSession`**: Manages multiple Codex runs with batch processing capabilities
- **`CodexRunResult`**: Contains complete results from a single run
- **`CodexSessionResult`**: Aggregates results from multiple runs

### Parsers

- **`CodexLogParser`**: Main parser for Codex log files with multiple extraction modes
- **`CodexOutputParser`**: Specialized parser for individual command outputs and responses

### Extractors

- **`PatchExtractor`**: Extracts patch/diff information from logs
- **`CommandExtractor`**: Extracts command execution data
- **`ToolUsageExtractor`**: Extracts tool usage information
- **`ChangeDetector`**: Detects various types of changes
- **`CustomExtractor`**: Create custom extraction patterns

### Data Models

- **`CodexChange`**: Represents detected changes
- **`PatchData`**: Represents patch/diff information
- **`CodexCommand`**: Represents executed commands
- **`ToolUsage`**: Represents tool usage data

### Utilities

- **`TemplateProcessor`**: Jinja2 template processing for prompts
- **`FileManager`**: File operations, backups, CSV handling
- **`DiffUtils`**: Diff creation and analysis utilities
- **`ColorUtils`**: Terminal color formatting

## Advanced Usage

### Custom Extractors

```python
from codex_interaction.extractors import CustomExtractor

# Create custom extractor
custom_extractor = CustomExtractor(
    pattern=r'ERROR:\s*(.+)',
    change_type="error"
)

# Use with parser
parser = CodexLogParser()
results = parser.parse_logs(extractors=[custom_extractor])
```

### File Filtering

```python
# Filter by file extension
results = parser.parse_logs()
csv_results = parser.filter_by_file_extension(results, '.csv')

# Filter by change type
patch_results = parser.filter_by_change_type(results, 'patch')
```

### Template Variables

```python
from codex_interaction.utils import TemplateProcessor

processor = TemplateProcessor()

# Convert CSV headers to Jinja variables
headers = ["File Path", "HTTP Method", "Priority Level"]
jinja_vars = processor.convert_csv_headers_to_jinja_vars(headers)
# Result: {"FILE_PATH": 0, "HTTP_METHOD": 1, "PRIORITY_LEVEL": 2}
```

## Design Philosophy

This library is designed with separation of concerns in mind:

1. **Pure Codex Interaction**: No UI or interface code, purely focused on Codex operations
2. **Reusable Components**: Each component can be used independently
3. **Comprehensive Parsing**: Extract all meaningful data from Codex operations
4. **Session Management**: Support both single runs and batch operations
5. **Extensible Architecture**: Easy to add new extractors and processors

## Use Cases

- **Automated Code Analysis**: Process multiple files/endpoints systematically
- **Log Analysis**: Analyze historical Codex operations and results
- **Batch Processing**: Execute multiple related Codex tasks in sequence
- **Template-driven Operations**: Use templates to generate consistent prompts
- **Integration Projects**: Embed Codex interaction into larger systems

## Dependencies

- `jinja2`: Template processing
- Standard library modules: `os`, `re`, `json`, `csv`, `subprocess`, `tempfile`, etc.

## License

This library is designed for use with other Codex-related projects and can be freely adapted for your needs. 