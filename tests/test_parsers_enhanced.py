"""
Enhanced tests for parsers module to achieve higher coverage.
Focuses on error handling, edge cases, and complex scenarios.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
from auto_codex.parsers import CodexLogParser, CodexOutputParser
from auto_codex.extractors import PatchExtractor, CustomExtractor
from auto_codex.models import DiscoveredTool


class TestCodexLogParserErrorHandling(unittest.TestCase):
    """Test error handling and edge cases in CodexLogParser."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.parser = CodexLogParser(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_parse_logs_with_unreadable_file(self):
        """Test parse_logs handles unreadable files gracefully."""
        # Create a log file that will cause read errors
        bad_file = os.path.join(self.temp_dir, "bad_log.log")
        with open(bad_file, 'w') as f:
            f.write("test content")
        
        self.parser.log_files = [bad_file]
        
        # Mock file read to raise exception
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            results = self.parser.parse_logs()
            # Should return empty list when file can't be read
            self.assertEqual(results, [])
    
    def test_parse_logs_with_file_filter_rejection(self):
        """Test parse_logs respects file filter."""
        # Create test log file
        log_file = os.path.join(self.temp_dir, "test.log")
        with open(log_file, 'w') as f:
            f.write("test content")
        
        self.parser.log_files = [log_file]
        
        # File filter that rejects all files
        def reject_all(file_path):
            return False
        
        results = self.parser.parse_logs(file_filter=reject_all)
        self.assertEqual(results, [])
    
    def test_parse_logs_with_content_filter_rejection(self):
        """Test parse_logs respects content filter."""
        # Create test log file
        log_file = os.path.join(self.temp_dir, "test.log")
        with open(log_file, 'w') as f:
            f.write("reject this content")
        
        self.parser.log_files = [log_file]
        
        # Content filter that rejects all content
        def reject_all_content(content):
            return False
        
        results = self.parser.parse_logs(content_filter=reject_all_content)
        self.assertEqual(results, [])
    
    def test_get_patches_error_handling(self):
        """Test get_patches handles errors gracefully."""
        # Mock parse_logs to raise exception
        with patch.object(self.parser, 'parse_logs', side_effect=Exception("Test error")):
            # Should not crash, but might propagate the exception
            with self.assertRaises(Exception):
                self.parser.get_patches()
    
    def test_to_dict_with_non_object(self):
        """Test _to_dict handles non-objects."""
        # Test with primitive types
        result = self.parser._to_dict("string")
        self.assertEqual(result, "string")
        
        result = self.parser._to_dict(123)
        self.assertEqual(result, 123)
        
        result = self.parser._to_dict(None)
        self.assertIsNone(result)
    
    def test_to_dict_with_enum_values(self):
        """Test _to_dict converts enum values properly."""
        # Create a mock object with enum attribute
        mock_obj = MagicMock()
        mock_obj.__dict__ = {"status": MagicMock()}
        mock_obj.__dict__["status"].value = "completed"
        
        result = self.parser._to_dict(mock_obj)
        self.assertEqual(result["status"], "completed")
    
    def test_parse_run_with_missing_file(self):
        """Test parse_run handles missing files."""
        non_existent_file = os.path.join(self.temp_dir, "nonexistent.log")
        
        result = self.parser.parse_run(non_existent_file)
        
        # Should return a valid CodexRunResult even with missing file
        self.assertIsNotNone(result)
        self.assertEqual(result.run_id, "nonexistent.log")
        self.assertEqual(result.log_file, non_existent_file)
    
    def test_parse_run_with_io_error(self):
        """Test parse_run handles file I/O errors."""
        log_file = os.path.join(self.temp_dir, "test.log")
        
        # Mock file operations to raise IOError
        with patch('builtins.open', side_effect=IOError("Disk error")):
            result = self.parser.parse_run(log_file)
            
            # Should return a valid result with error handling
            self.assertIsNotNone(result)
            self.assertEqual(result.log_file, log_file)
    
    def test_extract_start_time_with_invalid_timestamps(self):
        """Test _extract_start_time handles invalid timestamp formats."""
        content = "Invalid timestamp: 2024-13-45 25:99:99"
        log_file = os.path.join(self.temp_dir, "test.log")
        
        # Create the file so getmtime works
        with open(log_file, 'w') as f:
            f.write(content)
        
        result = self.parser._extract_start_time(content, log_file)
        
        # Should fall back to file modification time
        self.assertIsInstance(result, datetime)
    
    def test_extract_start_time_with_os_error(self):
        """Test _extract_start_time handles OS errors when getting file stats."""
        content = "No timestamp here"
        non_existent_file = "/nonexistent/path/file.log"
        
        result = self.parser._extract_start_time(content, non_existent_file)
        
        # Should fall back to current time
        self.assertIsInstance(result, datetime)
    
    def test_filter_by_file_extension_edge_cases(self):
        """Test filter_by_file_extension with edge cases."""
        results = [
            {"file_path": "test.py"},
            {"target_file": "script.js"},
            {"file_path": None},
            {"target_file": ""},
            {},  # No file path at all
        ]
        
        # Test with extension that has dot
        filtered = self.parser.filter_by_file_extension(results, ".py")
        self.assertEqual(len(filtered), 1)
        
        # Test with extension without dot
        filtered = self.parser.filter_by_file_extension(results, "js")
        self.assertEqual(len(filtered), 1)
        
        # Test with non-matching extension
        filtered = self.parser.filter_by_file_extension(results, ".txt")
        self.assertEqual(len(filtered), 0)
    
    def test_filter_by_change_type_edge_cases(self):
        """Test filter_by_change_type with edge cases."""
        results = [
            {"type": "patch"},
            {"type": "command"},
            {"type": None},
            {},  # No type field
        ]
        
        filtered = self.parser.filter_by_change_type(results, "patch")
        self.assertEqual(len(filtered), 1)
        
        # Test with non-existent type
        filtered = self.parser.filter_by_change_type(results, "nonexistent")
        self.assertEqual(len(filtered), 0)
    
    def test_create_custom_extractor(self):
        """Test create_custom_extractor method."""
        pattern = r"test_pattern"
        type_name = "test_type"
        
        extractor = self.parser.create_custom_extractor(pattern, type_name)
        
        self.assertIsInstance(extractor, CustomExtractor)
        # The pattern gets compiled as a regex
        self.assertEqual(extractor.pattern.pattern, pattern)
        self.assertEqual(extractor.change_type, type_name)
    
    def test_discover_tools_with_io_errors(self):
        """Test discover_tools handles I/O errors gracefully."""
        # Create a log file
        log_file = os.path.join(self.temp_dir, "test.log")
        with open(log_file, 'w') as f:
            f.write("test content")
        
        self.parser.log_files = [log_file]
        
        # Mock file read to raise exception
        with patch('builtins.open', side_effect=IOError("Read error")):
            result = self.parser.discover_tools()
            
            # Should return empty dict when files can't be read
            self.assertEqual(result, {})
    
    def test_discover_tools_with_empty_tool_names(self):
        """Test discover_tools handles empty tool names."""
        # Mock GenericToolExtractor to return tools with empty names
        mock_tool = DiscoveredTool(
            tool_name="",  # Empty tool name
            invocation="test_invocation",
            type="shell",
            log_file="test.log"
        )
        
        log_file = os.path.join(self.temp_dir, "test.log")
        with open(log_file, 'w') as f:
            f.write("test content")
        
        self.parser.log_files = [log_file]
        
        with patch('auto_codex.extractors.GenericToolExtractor.extract', return_value=[mock_tool]):
            result = self.parser.discover_tools()
            
            # Should skip tools with empty names
            self.assertEqual(result, {})
    
    def test_discover_tools_with_long_invocations(self):
        """Test discover_tools truncates long invocations."""
        # Create very long invocation
        long_invocation = "x" * 200  # Longer than 150 char limit
        
        mock_tool = DiscoveredTool(
            tool_name="test_tool",
            invocation=long_invocation,
            type="shell",
            log_file="test.log"
        )
        
        log_file = os.path.join(self.temp_dir, "test.log")
        with open(log_file, 'w') as f:
            f.write("test content")
        
        self.parser.log_files = [log_file]
        
        with patch('auto_codex.extractors.GenericToolExtractor.extract', return_value=[mock_tool]):
            result = self.parser.discover_tools()
            
            # Should truncate long examples
            self.assertIn("test_tool", result)
            example = result["test_tool"]["examples"][0]
            self.assertTrue(example.endswith("..."))
            self.assertLessEqual(len(example), 153)  # 150 + "..."


class TestCodexOutputParserErrorHandling(unittest.TestCase):
    """Test error handling and edge cases in CodexOutputParser."""
    
    def setUp(self):
        self.parser = CodexOutputParser()
    
    def test_parse_diff_with_malformed_content(self):
        """Test parse_diff handles malformed diff content."""
        malformed_diff = "This is not a valid diff\n+++malformed\n---incomplete"
        
        result = self.parser.parse_diff(malformed_diff)
        
        # Should handle gracefully
        self.assertIn('added', result)
        self.assertIn('removed', result)
        self.assertIn('is_diff', result)
        self.assertIsInstance(result['added'], int)
        self.assertIsInstance(result['removed'], int)
    
    def test_parse_diff_with_empty_content(self):
        """Test parse_diff handles empty content."""
        result = self.parser.parse_diff("")
        
        self.assertEqual(result['added'], 0)
        self.assertEqual(result['removed'], 0)
        self.assertFalse(result['is_diff'])
    
    def test_parse_command_output_edge_cases(self):
        """Test parse_command_output with various edge cases."""
        # Test with stderr but no stdout prefix - it splits on 'stderr:' but expects stdout: prefix
        output = "some output\nstderr: error message"
        result = self.parser.parse_command_output(output)
        self.assertEqual(result['stdout'], "")  # No stdout: prefix, so stdout is empty
        self.assertEqual(result['stderr'], "error message")
        
        # Test with both stdout and stderr prefixes
        output = "stdout: some output\nstderr: error message"
        result = self.parser.parse_command_output(output)
        self.assertEqual(result['stdout'], "some output")
        self.assertEqual(result['stderr'], "error message")
        
        # Test with empty output
        result = self.parser.parse_command_output("")
        self.assertEqual(result['stdout'], "")
        self.assertEqual(result['stderr'], "")
        
        # Test with only stderr
        output = "stderr: only error"
        result = self.parser.parse_command_output(output)
        self.assertEqual(result['stdout'], "")
        self.assertEqual(result['stderr'], "only error")
        
        # Test with stdout prefix
        output = "stdout: some output"
        result = self.parser.parse_command_output(output)
        self.assertEqual(result['stdout'], "some output")
        self.assertEqual(result['stderr'], "")
    
    def test_extract_suggested_edits_with_no_matches(self):
        """Test extract_suggested_edits when no edits are found."""
        content = "This is just regular text with no edit suggestions."
        
        result = self.parser.extract_suggested_edits(content)
        
        self.assertEqual(result, [])
    
    def test_extract_suggested_edits_with_malformed_patterns(self):
        """Test extract_suggested_edits with malformed patterns."""
        content = "edit_file target_file: incomplete pattern"
        
        result = self.parser.extract_suggested_edits(content)
        
        # Should handle gracefully without crashing
        self.assertIsInstance(result, list)
    
    def test_extract_suggested_edits_comprehensive(self):
        """Test extract_suggested_edits with various edit patterns."""
        content = '''
        edit_file target_file: "test.py"
        suggested edit file: script.js
        modify file: config.json
        '''
        
        result = self.parser.extract_suggested_edits(content)
        
        # Should find multiple edit suggestions
        self.assertGreater(len(result), 0)
        for edit in result:
            self.assertIn('type', edit)
            self.assertIn('file_path', edit)
            self.assertIn('context', edit)
            self.assertIn('line_number', edit)


if __name__ == '__main__':
    unittest.main() 