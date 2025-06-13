"""
Codex Interaction Library

A comprehensive library for interacting with Codex, parsing logs, and managing Codex runs.
Each run of Codex is represented as its own class with parsing capabilities for outputs.

Subpackages:
- auto_codex.benchmarks: LeetCode benchmarks for evaluating coding agents
- auto_codex.tests: Test suite for the auto_codex library
- auto_codex.examples: Example implementations and usage patterns
"""

from .core import CodexRun, CodexSession, SUPPORTED_PROVIDERS, validate_provider_config, get_provider_env_key
from .health import (
    AgentHealthMonitor,
    AgentHealthInfo,
    AgentStatus,
    HealthStatus,
    AgentMetrics,
    get_health_monitor,
    stop_global_monitor
)
from .parsers import CodexLogParser, CodexOutputParser
from .extractors import (
    PatchExtractor,
    CommandExtractor,
    ToolUsageExtractor,
    ChangeDetector
)
from .models import (
    CodexChange,
    CodexCommand,
    ToolUsage,
    PatchData
)
from .utils import (
    TemplateProcessor,
    FileManager,
    DiffUtils
)

__version__ = "1.0.0"
__all__ = [
    # Core classes
    "CodexRun",
    "CodexSession", 
    # Provider configuration
    "SUPPORTED_PROVIDERS",
    "validate_provider_config",
    "get_provider_env_key",
    # Health monitoring
    "AgentHealthMonitor",
    "AgentHealthInfo", 
    "AgentStatus",
    "HealthStatus",
    "AgentMetrics",
    "get_health_monitor",
    "stop_global_monitor",
    # Parsers
    "CodexLogParser",
    "CodexOutputParser",
    # Extractors
    "PatchExtractor",
    "CommandExtractor", 
    "ToolUsageExtractor",
    "ChangeDetector",
    # Data models
    "CodexChange",
    "CodexCommand",
    "ToolUsage", 
    "PatchData",
    # Utilities
    "TemplateProcessor",
    "FileManager",
    "DiffUtils"
] 