"""
Parser classes for handling Codex logs and output parsing.
"""

import os
import glob
import re
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime

from .models import CodexRunResult, ChangeType, ToolType, DiscoveredTool
from .extractors import (
    BaseExtractor, PatchExtractor, CommandExtractor, 
    ToolUsageExtractor, ChangeDetector, CustomExtractor, GenericToolExtractor
)


class CodexLogParser:
    """
    Enhanced parser for Codex log files with flexible extraction capabilities.
    
    Based on the original CodexLogParser but refactored for the library architecture.
    """
    
    def __init__(self, log_dir: str = ".", log_pattern: str = "codex_run_*.log"):
        """
        Initialize parser with log directory and pattern.
        
        Args:
            log_dir: Directory containing Codex log files
            log_pattern: Glob pattern for finding log files
        """
        self.log_dir = log_dir
        self.log_pattern = log_pattern
        self.log_files = self._find_log_files()
        
        # Default extractors
        self._default_extractors = [
            PatchExtractor(),
            CommandExtractor(),
            ToolUsageExtractor(),
            ChangeDetector()
        ]
    
    def _find_log_files(self) -> List[str]:
        """Find all Codex log files matching the pattern."""
        log_files = glob.glob(os.path.join(self.log_dir, self.log_pattern))
        return sorted(log_files)
    
    def get_log_files(self) -> List[str]:
        """Get list of found log files."""
        return self.log_files
    
    def parse_logs(self, 
                  extractors: Optional[List[BaseExtractor]] = None,
                  file_filter: Optional[Callable[[str], bool]] = None,
                  content_filter: Optional[Callable[[str], bool]] = None) -> List[Dict[str, Any]]:
        """
        Parse log files using provided extractors.
        
        Args:
            extractors: List of extractor instances to use
            file_filter: Optional function to filter log files by name
            content_filter: Optional function to filter log content
            
        Returns:
            List of extracted items from all logs
        """
        if not self.log_files:
            return []
        
        if extractors is None:
            extractors = self._default_extractors
        
        all_results = []
        
        for log_file in self.log_files:
            # Apply file filter if provided
            if file_filter and not file_filter(log_file):
                continue
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Apply content filter if provided
                if content_filter and not content_filter(content):
                    continue
                
                # Apply all extractors
                for extractor in extractors:
                    results = extractor.extract(log_file, content)
                    if results:
                        # Convert to dict format for backward compatibility
                        for result in results:
                            all_results.append(self._to_dict(result))
            
            except Exception as e:
                print(f"Error processing log file {log_file}: {e}")
        
        return all_results
    
    def get_patches(self) -> List[Dict[str, Any]]:
        """Convenience method to get all patches from logs."""
        patch_extractor = PatchExtractor()
        return self.parse_logs(extractors=[patch_extractor])
    
    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        """Convert extracted objects to dictionary format."""
        if hasattr(obj, '__dict__'):
            result = obj.__dict__.copy()
            # Convert enums to strings
            for key, value in result.items():
                if hasattr(value, 'value'):
                    result[key] = value.value
            return result
        return obj
    
    def parse_run(self, log_file: str, run_id: Optional[str] = None) -> CodexRunResult:
        """
        Parse a single log file into a CodexRunResult.
        
        Args:
            log_file: Path to the log file
            run_id: Optional run ID, defaults to log filename
            
        Returns:
            CodexRunResult with all extracted data
        """
        if run_id is None:
            run_id = os.path.basename(log_file)
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading log file {log_file}: {e}")
            return CodexRunResult(
                run_id=run_id,
                start_time=datetime.now(),
                log_file=log_file
            )
        
        # Extract using all extractors
        patch_extractor = PatchExtractor()
        command_extractor = CommandExtractor()
        tool_extractor = ToolUsageExtractor()
        change_extractor = ChangeDetector()
        
        patches = patch_extractor.extract(log_file, content)
        commands = command_extractor.extract(log_file, content)
        tool_usage = tool_extractor.extract(log_file, content)
        changes = change_extractor.extract(log_file, content)
        
        # Determine start time (try to extract from log or use file modification time)
        start_time = self._extract_start_time(content, log_file)
        
        return CodexRunResult(
            run_id=run_id,
            start_time=start_time,
            success=len(patches) > 0 or len(changes) > 0,  # Has some output
            changes=changes,
            commands=commands,
            tool_usage=tool_usage,
            patches=patches,
            log_file=log_file
        )
    
    def _extract_start_time(self, content: str, log_file: str) -> datetime:
        """Extract start time from log content or file stats."""
        # Try to find timestamp in log content
        timestamp_patterns = [
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
            r'(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})',
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    return datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        return datetime.strptime(match.group(1), '%Y/%m/%d %H:%M:%S')
                    except ValueError:
                        pass
        
        # Fall back to file modification time
        try:
            return datetime.fromtimestamp(os.path.getmtime(log_file))
        except OSError:
            return datetime.now()
    
    def filter_by_file_extension(self, results: List[Dict[str, Any]], extension: str) -> List[Dict[str, Any]]:
        """Filter results by file extension."""
        if not extension.startswith('.'):
            extension = '.' + extension
        
        filtered = []
        for result in results:
            file_path = result.get('file_path') or result.get('target_file')
            if file_path and file_path.endswith(extension):
                filtered.append(result)
        
        return filtered
    
    def filter_by_change_type(self, results: List[Dict[str, Any]], change_type: str) -> List[Dict[str, Any]]:
        """Filter results by change type."""
        return [r for r in results if r.get('type') == change_type]
    
    def create_custom_extractor(self, pattern: str, type_name: str) -> CustomExtractor:
        """Create a custom extractor with the given pattern."""
        return CustomExtractor(pattern, type_name)

    def discover_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Discovers all unique tools used in the logs and provides examples.

        Returns:
            A dictionary where keys are tool names and values are details
            about the tool (count and example invocations).
        """
        tool_extractor = GenericToolExtractor()
        all_tool_uses = []

        for log_file in self.log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                results = tool_extractor.extract(log_file, content)
                if results:
                    all_tool_uses.extend(results)
            except Exception as e:
                print(f"Error processing log file {log_file}: {e}")
        
        discovered_tools = {}
        for tool_use in all_tool_uses:
            tool_name = tool_use.tool_name
            if not tool_name:
                continue

            if tool_name not in discovered_tools:
                discovered_tools[tool_name] = {
                    "count": 0,
                    "examples": set(),
                    "type": set()
                }

            discovered_tools[tool_name]["count"] += 1
            discovered_tools[tool_name]["type"].add(tool_use.type)
            
            invocation = tool_use.invocation
            if invocation and len(discovered_tools[tool_name]["examples"]) < 5:
                example = str(invocation)
                if len(example) > 150:
                    example = example[:150] + "..."
                discovered_tools[tool_name]["examples"].add(example)
        
        # Convert sets to lists for easier display
        for tool in discovered_tools.values():
            tool["examples"] = sorted(list(tool["examples"]))
            tool["type"] = sorted(list(tool["type"]))
            
        return discovered_tools


class CodexOutputParser:
    """
    Parses various types of output that Codex might produce,
    such as diffs or command results.
    """
    
    def __init__(self):
        """Initialize the output parser."""
        self.diff_pattern = re.compile(r'^(--- a/.*?\n\+\+\+ b/.*?$)', re.MULTILINE)
    
    def parse_diff(self, diff_content: str) -> Dict[str, Any]:
        """
        Parse a diff string to extract added and removed lines.
        
        Args:
            diff_content: The diff string
            
        Returns:
            Dictionary with counts of added/removed lines
        """
        added = len([
            line for line in diff_content.splitlines() 
            if line.strip().startswith('+') and not line.strip().startswith('+++')
        ])
        removed = len([
            line for line in diff_content.splitlines() 
            if line.strip().startswith('-') and not line.strip().startswith('---')
        ])
        
        return {
            'added': added,
            'removed': removed,
            'is_diff': bool(self.diff_pattern.search(diff_content))
        }
    
    def parse_command_output(self, output: str) -> Dict[str, Any]:
        """
        Parse the output of a command into stdout and stderr.
        
        Args:
            output: The command output string
            
        Returns:
            Dictionary with stdout and stderr
        """
        stdout = ''
        stderr = ''
        
        if 'stderr:' in output:
            parts = output.split('stderr:', 1)
            stdout_part = parts[0]
            stderr = parts[1].strip()
            
            if stdout_part.startswith('stdout:'):
                stdout = stdout_part[len('stdout:'):].strip()
        elif output.startswith('stdout:'):
            stdout = output[len('stdout:'):].strip()
        else:
            stdout = output.strip()
            
        return {'stdout': stdout, 'stderr': stderr}
    
    def extract_suggested_edits(self, content: str) -> List[Dict[str, Any]]:
        """
        Extracts suggested edits from a block of text.
        
        Args:
            content: The block of text to parse for suggested edits
            
        Returns:
            List of suggested edit dictionaries
        """
        edits = []
        
        # Pattern for detecting edit suggestions
        edit_patterns = [
            r'edit_file.*?target_file["\']:\s*["\']([^"\']+)["\']',
            r'suggested.*?edit.*?file[:\s]+([^\s\n]+)',
            r'modify.*?file[:\s]+([^\s\n]+)',
        ]
        
        for pattern in edit_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                edits.append({
                    'type': 'edit_suggestion',
                    'file_path': match.group(1),
                    'context': match.group(0),
                    'line_number': content[:match.start()].count('\n') + 1
                })
        
        return edits 