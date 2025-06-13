"""
Data models for representing Codex operations and outputs.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum


class ChangeType(Enum):
    """Types of changes that can be detected."""
    PATCH = "patch"
    COMMAND = "command" 
    TOOL_USE = "tool_use"
    CHANGES_DETECTED = "changes_detected"
    CUSTOM = "custom"


class ToolType(Enum):
    """Types of tools used by Codex."""
    EDIT = "edit"
    READ = "read"
    SEARCH = "search"
    LIST = "list"
    DELETE = "delete"
    RUN = "run"
    CREATE = "create"
    WEB = "web"
    UNKNOWN = "unknown"


@dataclass
class CodexChange:
    """Represents a change detected in Codex logs."""
    type: ChangeType
    log_file: str
    content: str
    timestamp: Optional[datetime] = None
    file_path: Optional[str] = None
    raw_match: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = ChangeType(self.type)


@dataclass
class PatchData:
    """Represents patch/diff information from Codex."""
    file_path: str
    diff_content: str
    log_file: str
    lines_added: int = 0
    lines_removed: int = 0
    raw_patch: Optional[str] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.diff_content:
            self._parse_diff_stats()

    def _parse_diff_stats(self):
        """Parse diff content to count added/removed lines."""
        for line in self.diff_content.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                self.lines_added += 1
            elif line.startswith('-') and not line.startswith('---'):
                self.lines_removed += 1


@dataclass
class CodexCommand:
    """Represents a command executed by Codex."""
    command: str
    log_file: str
    tool_name: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    output: Optional[str] = None
    exit_code: Optional[int] = None
    timestamp: Optional[datetime] = None
    target_files: List[str] = field(default_factory=list)

    def is_successful(self) -> bool:
        """Check if command executed successfully."""
        return self.exit_code == 0 if self.exit_code is not None else None


@dataclass
class ToolUsage:
    """Represents usage of a specific tool by Codex."""
    tool_name: str
    tool_type: ToolType
    log_file: str
    target_file: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    operation: Optional[str] = None
    timestamp: Optional[datetime] = None
    success: Optional[bool] = None

    def __post_init__(self):
        if isinstance(self.tool_type, str):
            try:
                self.tool_type = ToolType(self.tool_type)
            except ValueError:
                self.tool_type = ToolType.UNKNOWN


@dataclass
class CodexRunResult:
    """Represents the complete result of a Codex run."""
    run_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    changes: List[CodexChange] = field(default_factory=list)
    commands: List[CodexCommand] = field(default_factory=list)
    tool_usage: List[ToolUsage] = field(default_factory=list)
    patches: List[PatchData] = field(default_factory=list)
    log_file: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        """Get duration of the run in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def files_modified(self) -> List[str]:
        """Get list of unique files that were modified."""
        files = set()
        for change in self.changes:
            if change.file_path:
                files.add(change.file_path)
        for patch in self.patches:
            files.add(patch.file_path)
        for tool in self.tool_usage:
            if tool.target_file:
                files.add(tool.target_file)
        return sorted(list(files))

    def get_changes_by_type(self, change_type: ChangeType) -> List[CodexChange]:
        """Get changes filtered by type."""
        return [c for c in self.changes if c.type == change_type]

    def get_tools_by_type(self, tool_type: ToolType) -> List[ToolUsage]:
        """Get tool usage filtered by type."""
        return [t for t in self.tool_usage if t.tool_type == tool_type]


@dataclass
class CodexSessionResult:
    """Represents results from multiple Codex runs in a session."""
    session_id: str
    runs: List[CodexRunResult] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @property
    def total_files_modified(self) -> List[str]:
        """Get total unique files modified across all runs."""
        files = set()
        for run in self.runs:
            if run is not None:  # Handle None run results
                files.update(run.files_modified)
        return sorted(list(files))

    @property
    def total_changes(self) -> int:
        """Get total number of changes across all runs."""
        return sum(len(run.changes) for run in self.runs if run is not None)

    @property
    def successful_runs(self) -> List[CodexRunResult]:
        """Get only successful runs."""
        return [run for run in self.runs if run is not None and run.success]

    def get_runs_by_file(self, file_path: str) -> List[CodexRunResult]:
        """Get runs that modified a specific file."""
        return [run for run in self.runs if run is not None and file_path in run.files_modified]


@dataclass
class DiscoveredTool:
    """Represents a discovered tool invocation."""
    tool_name: str
    invocation: Any
    type: str  # 'shell' or 'function_call'
    log_file: str 