"""
Extractor classes for parsing different types of Codex output data.
"""

import re
import json
import os
from typing import Dict, List, Optional, Any, Pattern
from datetime import datetime

from .models import (
    CodexChange, PatchData, CodexCommand, ToolUsage, 
    ChangeType, ToolType, DiscoveredTool
)


class BaseExtractor:
    """Base class for all extractors."""
    
    def __init__(self, file_pattern: Optional[str] = None):
        """
        Initialize extractor with optional file pattern filter.
        
        Args:
            file_pattern: Regex pattern to match file paths
        """
        self.file_pattern = re.compile(file_pattern) if file_pattern else None
    
    def extract(self, log_file: str, content: str) -> List[Any]:
        """Extract data from log content. To be implemented by subclasses."""
        raise NotImplementedError
    
    def _matches_file_pattern(self, file_path: str) -> bool:
        """Check if file path matches the configured pattern."""
        if not self.file_pattern:
            return True
        return bool(self.file_pattern.search(file_path))


class PatchExtractor(BaseExtractor):
    """Extract patch/diff changes from Codex logs."""
    
    def extract(self, log_file: str, content: str) -> List[PatchData]:
        """Extract patch information from log content."""
        results = []
        # This regex looks for Add File or Update File, then the file path, then the patch content
        patch_pattern = re.compile(
            r"\*\*\* (?:Add|Update) File: (.*?)\n(.*?)\*\*\* End Patch",
            re.DOTALL | re.IGNORECASE
        )

        for line in content.splitlines():
            try:
                log_entry = json.loads(line)
                
                if log_entry.get('name') == 'shell' and 'arguments' in log_entry:
                    args_str = log_entry.get('arguments', '{}')
                    
                    try:
                        args = json.loads(args_str)
                    except json.JSONDecodeError:
                        continue

                    command_list = args.get('command', [])
                    
                    if command_list and command_list[0] == 'apply_patch' and len(command_list) > 1:
                        # The patch content has escaped newlines, so we un-escape them
                        raw_patch = command_list[1].replace('\\n', '\n')
                        
                        match = patch_pattern.search(raw_patch)
                        if match:
                            file_path = match.group(1).strip()
                            # The second group will contain the diff content up to the "End Patch"
                            diff_content = match.group(2).strip()
                            
                            if self._matches_file_pattern(file_path):
                                results.append(PatchData(
                                    file_path=file_path,
                                    diff_content=diff_content,
                                    log_file=os.path.basename(log_file),
                                    raw_patch=command_list[1]  # Store original
                                ))

            except (json.JSONDecodeError, KeyError, TypeError, IndexError):
                continue
        
        return results


class CommandExtractor(BaseExtractor):
    """Extract command execution information from Codex logs."""
    
    def extract(self, log_file: str, content: str) -> List[CodexCommand]:
        """Extract command information from log content."""
        results = []
        
        for line_num, line in enumerate(content.split('\n'), 1):
            # Look for any JSON that could represent a tool/command invocation
            if any(keyword in line for keyword in ['function_call', 'tool_use', 'tool_call']):
                try:
                    json_obj = json.loads(line)
                    command = self._parse_command_json(json_obj, log_file, line_num)
                    if command:
                        results.append(command)
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return results
    
    def _parse_command_json(self, json_obj: Dict[str, Any], log_file: str, line_num: int) -> Optional[CodexCommand]:
        """Parse a JSON object to extract command information."""
        if 'arguments' not in json_obj:
            return None
        
        tool_name = json_obj.get('name', '')
        
        # Parse arguments (could be string or object)
        try:
            if isinstance(json_obj['arguments'], str):
                args = json.loads(json_obj['arguments'])
            else:
                args = json_obj['arguments']
        except (json.JSONDecodeError, TypeError):
            args = json_obj['arguments']
        
        # Extract command and target files
        command = args.get('command', '') if isinstance(args, dict) else str(args)
        target_files = []
        
        if isinstance(args, dict):
            # Look for various file-related arguments
            file_keys = ['target_file', 'file_path', 'filename', 'path']
            for key in file_keys:
                if key in args and args[key]:
                    target_files.append(args[key])
        
        return CodexCommand(
            command=command,
            log_file=os.path.basename(log_file),
            tool_name=tool_name,
            arguments=args,
            target_files=target_files
        )


class ToolUsageExtractor(BaseExtractor):
    """Extract tool usage information from Codex logs."""
    
    def extract(self, log_file: str, content: str) -> List[ToolUsage]:
        """Extract tool usage information from log content."""
        results = []
        
        for line in content.split('\n'):
            # Look for tool usage patterns
            if any(keyword in line for keyword in ['function_call', 'tool_use', 'tool_call']):
                try:
                    json_obj = json.loads(line)
                    tool_usage = self._parse_tool_usage(json_obj, log_file)
                    if tool_usage:
                        results.append(tool_usage)
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return results
    
    def _parse_tool_usage(self, json_obj: Dict[str, Any], log_file: str) -> Optional[ToolUsage]:
        """Parse JSON object to extract tool usage information."""
        tool_name = json_obj.get('name', '')
        if not tool_name:
            return None
        
        # Categorize tool type
        tool_type = self._categorize_tool(tool_name)
        
        # Parse arguments
        try:
            if isinstance(json_obj.get('arguments'), str):
                args = json.loads(json_obj['arguments'])
            else:
                args = json_obj.get('arguments', {})
        except (json.JSONDecodeError, TypeError):
            args = {}
        
        # Extract target file
        target_file = None
        if isinstance(args, dict):
            file_keys = ['target_file', 'file_path', 'filename', 'path']
            for key in file_keys:
                if key in args and args[key]:
                    target_file = args[key]
                    break
        
        return ToolUsage(
            tool_name=tool_name,
            tool_type=tool_type,
            log_file=os.path.basename(log_file),
            target_file=target_file,
            arguments=args
        )
    
    def _categorize_tool(self, tool_name: str) -> ToolType:
        """Categorize a tool by its name."""
        name_lower = tool_name.lower()
        
        if any(word in name_lower for word in ['edit', 'write', 'modify', 'update']):
            return ToolType.EDIT
        elif any(word in name_lower for word in ['read', 'cat', 'view', 'show']):
            return ToolType.READ
        elif any(word in name_lower for word in ['search', 'grep', 'find', 'query']):
            return ToolType.SEARCH
        elif any(word in name_lower for word in ['list', 'ls', 'dir', 'tree']):
            return ToolType.LIST
        elif any(word in name_lower for word in ['delete', 'remove', 'rm']):
            return ToolType.DELETE
        elif any(word in name_lower for word in ['run', 'exec', 'command', 'terminal']):
            return ToolType.RUN
        elif any(word in name_lower for word in ['create', 'new', 'make', 'mkdir']):
            return ToolType.CREATE
        elif any(word in name_lower for word in ['web', 'browser', 'http', 'url']):
            return ToolType.WEB
        else:
            return ToolType.UNKNOWN


class ChangeDetector(BaseExtractor):
    """Detect various types of changes in Codex logs."""
    
    def extract(self, log_file: str, content: str) -> List[CodexChange]:
        """Extract change information from log content by parsing JSON."""
        results = []
        for line in content.splitlines():
            try:
                log_entry = json.loads(line)
                if log_entry.get('type') == 'codex_change':
                    change_type_str = log_entry.get('change_type', 'unknown')
                    file_path = log_entry.get('file_path')
                    
                    if file_path and self._matches_file_pattern(file_path):
                        results.append(CodexChange(
                            type=ChangeType(change_type_str),
                            log_file=os.path.basename(log_file),
                            content=log_entry.get('content', ''),
                            file_path=file_path,
                            raw_match=line
                        ))
            except (json.JSONDecodeError, KeyError, ValueError):
                # Also handles cases where change_type_str is not a valid ChangeType
                continue
        return results


class CustomExtractor(BaseExtractor):
    """Extract custom patterns from Codex logs."""
    
    def __init__(self, pattern: str, change_type: str = "custom", file_pattern: Optional[str] = None):
        """
        Initialize with custom regex pattern.
        
        Args:
            pattern: Regex pattern to match
            change_type: Type name for matched changes
            file_pattern: Optional file pattern filter
        """
        super().__init__(file_pattern)
        self.pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        self.change_type = ChangeType.CUSTOM if change_type == "custom" else change_type
    
    def extract(self, log_file: str, content: str) -> List[CodexChange]:
        """Extract custom pattern matches from log content."""
        results = []
        
        for match in self.pattern.finditer(content):
            results.append(CodexChange(
                type=self.change_type,
                log_file=os.path.basename(log_file),
                content=match.group(0),
                raw_match=match.groups() if match.groups() else match.group(0)
            ))
        
        return results


class GenericToolExtractor(BaseExtractor):
    """Extract all tool calls, regardless of type."""

    def extract(self, log_file: str, content: str) -> List[Any]:
        """Extract all tool usage from log content."""
        results = []
        for line in content.splitlines():
            if any(keyword in line for keyword in ['function_call', 'tool_use', 'tool_call']):
                try:
                    log_entry = json.loads(line)
                    tool_name = log_entry.get('name')
                    if tool_name:
                         results.append(DiscoveredTool(
                            tool_name=tool_name,
                            invocation=log_entry['arguments'],
                            type="function_call",
                            log_file=os.path.basename(log_file)
                        ))
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return results 