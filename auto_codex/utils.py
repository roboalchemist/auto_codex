"""
Utility classes for template processing, file management, and diff operations.
"""

import os
import re
import shutil
import tempfile
import csv
import difflib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

import jinja2


class TemplateProcessor:
    """
    Handles Jinja2 template processing for Codex prompts and other templating needs.
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize template processor.
        
        Args:
            template_dir: Directory containing template files (defaults to 'prompts')
        """
        self.template_dir = template_dir or "prompts"
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir) if os.path.exists(self.template_dir) else None,
            autoescape=False
        )
    
    @staticmethod
    def convert_csv_headers_to_jinja_vars(headers: List[str]) -> Dict[str, int]:
        """
        Convert CSV headers to Jinja2 variable format (UPPER_SNAKE_CASE).
        
        Args:
            headers: List of CSV column headers
            
        Returns:
            Dictionary mapping Jinja variables to column indices
        """
        jinja_vars = {}
        for i, header in enumerate(headers):
            # Strip whitespace and replace remaining spaces with underscores
            var = re.sub(r'\s+', '_', header.strip())
            # Convert to uppercase
            var = var.upper()
            jinja_vars[var] = i
        return jinja_vars
    
    def load_template_file(self, template_name: str) -> str:
        """
        Load a template file from the template directory.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            Template content as string
        """
        # Try to find the template file with various extensions
        template_path = self._find_template_file(template_name)
        
        if not template_path:
            raise FileNotFoundError(f"Template file '{template_name}' not found in {self.template_dir}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _find_template_file(self, template_name: str) -> Optional[str]:
        """Find a template file with various possible extensions."""
        if os.path.isfile(template_name):
            return template_name
        
        # Check if the template is in the template directory
        template_path = os.path.join(self.template_dir, template_name)
        if os.path.isfile(template_path):
            return template_path
        
        # Try adding extensions
        for ext in [".txt", ".j2", ".jinja2"]:
            # Try with template directory
            ext_path = os.path.join(self.template_dir, template_name + ext)
            if os.path.isfile(ext_path):
                return ext_path
            
            # Try without template directory
            ext_path = template_name + ext
            if os.path.isfile(ext_path):
                return ext_path
        
        return None
    
    def render_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """
        Render a Jinja2 template with the provided variables.
        
        Args:
            template_content: Template string to render
            variables: Variables to use in template rendering
            
        Returns:
            Rendered template string
        """
        try:
            template = jinja2.Template(template_content)
            return template.render(**variables)
        except jinja2.TemplateError as e:
            raise ValueError(f"Template rendering error: {e}")
    
    def render_template_file(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Load and render a template file.
        
        Args:
            template_name: Name of the template file
            variables: Variables to use in template rendering
            
        Returns:
            Rendered template string
        """
        template_content = self.load_template_file(template_name)
        return self.render_template(template_content, variables)
    
    def create_csv_variables(self, csv_row: List[str], headers: List[str]) -> Dict[str, str]:
        """
        Create template variables from a CSV row.
        
        Args:
            csv_row: List of values from a CSV row
            headers: List of CSV headers
            
        Returns:
            Dictionary of template variables
        """
        jinja_vars = self.convert_csv_headers_to_jinja_vars(headers)
        
        # Create template variables from the row
        variables = {}
        for var_name, col_idx in jinja_vars.items():
            if col_idx < len(csv_row):
                variables[var_name] = csv_row[col_idx]
            else:
                variables[var_name] = ""
        
        return variables


class FileManager:
    """
    Handles file operations, backups, and directory management for Codex operations.
    """
    
    def __init__(self, working_dir: Optional[str] = None):
        """
        Initialize file manager.
        
        Args:
            working_dir: Working directory for file operations
        """
        self.working_dir = working_dir or os.getcwd()
    
    def create_backup(self, file_path: str, backup_suffix: str = ".bak") -> str:
        """
        Create a backup of a file.
        
        Args:
            file_path: Path to the file to backup
            backup_suffix: Suffix for the backup file
            
        Returns:
            Path to the backup file
        """
        backup_path = file_path + backup_suffix
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def create_timestamped_backup(self, file_path: str) -> str:
        """
        Create a timestamped backup of a file.
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            Path to the backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.{timestamp}.bak"
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def load_csv_file(self, csv_file: str) -> Tuple[List[str], List[List[str]]]:
        """
        Load a CSV file and return headers and rows.
        
        Args:
            csv_file: Path to the CSV file
            
        Returns:
            Tuple of (headers, rows)
        """
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            rows = list(reader)
        
        return headers, rows
    
    def save_csv_file(self, csv_file: str, headers: List[str], rows: List[List[str]]):
        """
        Save data to a CSV file.
        
        Args:
            csv_file: Path to the CSV file
            headers: List of column headers
            rows: List of rows (each row is a list of values)
        """
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
    
    def create_temporary_directory(self) -> str:
        """
        Create a temporary directory for Codex operations.
        
        Returns:
            Path to the temporary directory
        """
        return tempfile.mkdtemp(prefix="codex_")
    
    def copy_directory_structure(self, src_dir: str, dst_dir: str, file_pattern: Optional[str] = None):
        """
        Copy directory structure and optionally filter files.
        
        Args:
            src_dir: Source directory
            dst_dir: Destination directory
            file_pattern: Optional regex pattern to filter files
        """
        os.makedirs(dst_dir, exist_ok=True)
        
        for root, dirs, files in os.walk(src_dir):
            # Calculate relative path
            rel_path = os.path.relpath(root, src_dir)
            if rel_path == '.':
                dest_root = dst_dir
            else:
                dest_root = os.path.join(dst_dir, rel_path)
                os.makedirs(dest_root, exist_ok=True)
            
            # Copy files
            for file in files:
                if file_pattern and not re.search(file_pattern, file):
                    continue
                
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dest_root, file)
                shutil.copy2(src_file, dst_file)
    
    def ensure_directory_exists(self, directory: str):
        """
        Ensure that a directory exists, creating it if necessary.
        
        Args:
            directory: Path to the directory
        """
        os.makedirs(directory, exist_ok=True)


class DiffUtils:
    """
    Utilities for handling diffs and comparing files.
    """
    
    @staticmethod
    def create_unified_diff(original_file: str, modified_file: str, 
                          fromfile: str = "original", tofile: str = "modified") -> List[str]:
        """
        Create a unified diff between two files.
        
        Args:
            original_file: Path to the original file
            modified_file: Path to the modified file
            fromfile: Label for the original file
            tofile: Label for the modified file
            
        Returns:
            List of diff lines
        """
        with open(original_file, 'r', encoding='utf-8') as f:
            original_lines = f.readlines()
        
        with open(modified_file, 'r', encoding='utf-8') as f:
            modified_lines = f.readlines()
        
        return list(difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=fromfile,
            tofile=tofile,
            lineterm=''
        ))
    
    @staticmethod
    def format_diff_for_display(diff_lines: List[str]) -> List[Tuple[str, str]]:
        """
        Format diff lines for colored display.
        
        Args:
            diff_lines: List of diff lines
            
        Returns:
            List of (line, color) tuples
        """
        formatted_lines = []
        
        for line in diff_lines:
            if line.startswith('+'):
                formatted_lines.append((line, 'green'))
            elif line.startswith('-'):
                formatted_lines.append((line, 'red'))
            elif line.startswith('@@'):
                formatted_lines.append((line, 'cyan'))
            elif line.startswith('+++') or line.startswith('---'):
                formatted_lines.append((line, 'yellow'))
            else:
                formatted_lines.append((line, 'white'))
        
        return formatted_lines
    
    @staticmethod
    def has_changes(diff_lines: List[str]) -> bool:
        """
        Check if diff lines contain actual changes.
        
        Args:
            diff_lines: List of diff lines
            
        Returns:
            True if there are changes, False otherwise
        """
        return any(line.startswith(('+', '-')) and not line.startswith(('+++', '---')) 
                  for line in diff_lines)
    
    @staticmethod
    def parse_diff_stats(diff_content: str) -> Dict[str, int]:
        """
        Parse diff content to extract statistics.
        
        Args:
            diff_content: Raw diff content
            
        Returns:
            Dictionary with diff statistics
        """
        lines = diff_content.split('\n')
        stats = {
            'lines_added': 0,
            'lines_removed': 0,
            'hunks': 0
        }
        
        for line in lines:
            if line.startswith('+') and not line.startswith('+++'):
                stats['lines_added'] += 1
            elif line.startswith('-') and not line.startswith('---'):
                stats['lines_removed'] += 1
            elif line.startswith('@@'):
                stats['hunks'] += 1
        
        return stats
    
    @staticmethod
    def extract_file_paths_from_diff(diff_content: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract file paths from diff headers.
        
        Args:
            diff_content: Raw diff content
            
        Returns:
            Tuple of (original_file_path, modified_file_path)
        """
        lines = diff_content.split('\n')
        original_file = None
        modified_file = None
        
        for line in lines:
            if line.startswith('---'):
                # Extract file path after "--- "
                match = re.match(r'---\s+(.+)', line)
                if match:
                    original_file = match.group(1).strip()
            elif line.startswith('+++'):
                # Extract file path after "+++ "
                match = re.match(r'\+\+\+\s+(.+)', line)
                if match:
                    modified_file = match.group(1).strip()
        
        return original_file, modified_file


class ColorUtils:
    """
    Utilities for colored terminal output.
    """
    
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m',
        'bold': '\033[1m'
    }
    
    @classmethod
    def colorize(cls, text: str, color: str, bold: bool = False) -> str:
        """
        Add color formatting to text.
        
        Args:
            text: Text to colorize
            color: Color name
            bold: Whether to make text bold
            
        Returns:
            Colored text string
        """
        if color not in cls.COLORS:
            return text
        
        result = cls.COLORS[color] + text + cls.COLORS['reset']
        if bold:
            result = cls.COLORS['bold'] + result
        
        return result
    
    @classmethod
    def print_colored_diff(cls, diff_lines: List[Tuple[str, str]]):
        """
        Print colored diff lines.
        
        Args:
            diff_lines: List of (line, color) tuples
        """
        for line, color in diff_lines:
            print(cls.colorize(line, color)) 