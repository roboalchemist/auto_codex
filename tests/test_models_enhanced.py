"""
Enhanced tests for models module to achieve higher coverage.
Focuses on error handling, edge cases, and property validation.
"""

import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
from auto_codex.models import (
    ChangeType, ToolType, CodexChange, PatchData, CodexCommand, 
    ToolUsage, CodexRunResult, CodexSessionResult, DiscoveredTool
)


class TestCodexChangeErrorHandling(unittest.TestCase):
    """Test error handling in CodexChange."""
    
    def test_post_init_with_invalid_string_type(self):
        """Test __post_init__ handles invalid string types."""
        # Test with invalid enum string
        with self.assertRaises(ValueError):
            CodexChange(
                type="invalid_type",  # This should trigger ValueError
                log_file="test.log",
                content="test content"
            )
    
    def test_post_init_with_valid_enum(self):
        """Test __post_init__ works with valid enum."""
        change = CodexChange(
            type=ChangeType.PATCH,  # Already enum
            log_file="test.log",
            content="test content"
        )
        self.assertEqual(change.type, ChangeType.PATCH)


class TestPatchDataErrorHandling(unittest.TestCase):
    """Test error handling in PatchData."""
    
    def test_parse_diff_stats_with_empty_content(self):
        """Test _parse_diff_stats handles empty diff content."""
        patch = PatchData(
            file_path="test.py",
            diff_content="",  # Empty content
            log_file="test.log"
        )
        
        self.assertEqual(patch.lines_added, 0)
        self.assertEqual(patch.lines_removed, 0)
    
    def test_parse_diff_stats_with_malformed_diff(self):
        """Test _parse_diff_stats handles malformed diff content."""
        malformed_diff = """
        This is not a proper diff
        +++ some text
        --- some other text
        random content
        """
        
        patch = PatchData(
            file_path="test.py",
            diff_content=malformed_diff,
            log_file="test.log"
        )
        
        # Should handle gracefully without crashing
        self.assertIsInstance(patch.lines_added, int)
        self.assertIsInstance(patch.lines_removed, int)

    def test_parse_diff_stats_with_valid_diff_additions(self):
        """Test _parse_diff_stats correctly counts added lines."""
        valid_diff = """
--- a/test.py
+++ b/test.py
@@ -1,3 +1,6 @@
 def function():
+    # This is a new line
+    new_variable = 42
     existing_line()
+    another_new_line()
"""
        
        patch = PatchData(
            file_path="test.py",
            diff_content=valid_diff,
            log_file="test.log"
        )
        
        # Should count 3 added lines (lines starting with + but not +++)
        self.assertEqual(patch.lines_added, 3)
        self.assertEqual(patch.lines_removed, 0)

    def test_parse_diff_stats_with_valid_diff_deletions(self):
        """Test _parse_diff_stats correctly counts removed lines."""
        valid_diff = """
--- a/test.py
+++ b/test.py
@@ -1,5 +1,2 @@
 def function():
-    old_line_1()
-    old_line_2()
     existing_line()
-    another_old_line()
"""
        
        patch = PatchData(
            file_path="test.py",
            diff_content=valid_diff,
            log_file="test.log"
        )
        
        # Should count 3 removed lines (lines starting with - but not ---)
        self.assertEqual(patch.lines_added, 0)
        self.assertEqual(patch.lines_removed, 3)

    def test_parse_diff_stats_with_mixed_changes(self):
        """Test _parse_diff_stats with both additions and deletions."""
        mixed_diff = """
--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
 def function():
-    old_implementation()
+    new_implementation()
+    extra_feature()
     existing_line()
-    deprecated_method()
"""
        
        patch = PatchData(
            file_path="test.py",
            diff_content=mixed_diff,
            log_file="test.log"
        )
        
        # Should count both additions and deletions correctly
        self.assertEqual(patch.lines_added, 2)
        self.assertEqual(patch.lines_removed, 2)

    def test_patch_data_without_diff_content(self):
        """Test PatchData initialization without diff content."""
        patch = PatchData(
            file_path="test.py",
            diff_content=None,  # No diff content
            log_file="test.log"
        )
        
        # Should not call _parse_diff_stats and leave counters at 0
        self.assertEqual(patch.lines_added, 0)
        self.assertEqual(patch.lines_removed, 0)


class TestCodexCommandErrorHandling(unittest.TestCase):
    """Test error handling in CodexCommand."""
    
    def test_is_successful_with_none_exit_code(self):
        """Test is_successful returns None when exit_code is None."""
        command = CodexCommand(
            command="test command",
            log_file="test.log",
            exit_code=None  # No exit code available
        )
        
        result = command.is_successful()
        self.assertIsNone(result)
    
    def test_is_successful_with_zero_exit_code(self):
        """Test is_successful returns True for exit code 0."""
        command = CodexCommand(
            command="test command",
            log_file="test.log",
            exit_code=0
        )
        
        result = command.is_successful()
        self.assertTrue(result)
    
    def test_is_successful_with_non_zero_exit_code(self):
        """Test is_successful returns False for non-zero exit code."""
        command = CodexCommand(
            command="test command",
            log_file="test.log",
            exit_code=1
        )
        
        result = command.is_successful()
        self.assertFalse(result)


class TestToolUsageErrorHandling(unittest.TestCase):
    """Test error handling in ToolUsage."""
    
    def test_post_init_with_invalid_tool_type_string(self):
        """Test __post_init__ handles invalid tool type strings."""
        tool_usage = ToolUsage(
            tool_name="invalid_tool",
            tool_type="invalid_type",  # Invalid string
            log_file="test.log"
        )
        
        # Should fall back to UNKNOWN
        self.assertEqual(tool_usage.tool_type, ToolType.UNKNOWN)
    
    def test_post_init_with_valid_enum(self):
        """Test __post_init__ works with valid enum."""
        tool_usage = ToolUsage(
            tool_name="test_tool",
            tool_type=ToolType.EDIT,  # Already valid enum
            log_file="test.log"
        )
        
        self.assertEqual(tool_usage.tool_type, ToolType.EDIT)
    
    def test_post_init_with_valid_string(self):
        """Test __post_init__ converts valid string to enum."""
        tool_usage = ToolUsage(
            tool_name="test_tool",
            tool_type="edit",  # Valid string
            log_file="test.log"
        )
        
        self.assertEqual(tool_usage.tool_type, ToolType.EDIT)

    def test_post_init_successful_enum_conversion(self):
        """Test __post_init__ successfully converts all valid enum strings."""
        # Test all valid ToolType enum values as strings
        valid_tool_types = [
            ("edit", ToolType.EDIT),
            ("read", ToolType.READ),
            ("search", ToolType.SEARCH),
            ("list", ToolType.LIST),
            ("delete", ToolType.DELETE),
            ("run", ToolType.RUN),
            ("create", ToolType.CREATE),
            ("web", ToolType.WEB),
            ("unknown", ToolType.UNKNOWN),
        ]
        
        for string_value, expected_enum in valid_tool_types:
            with self.subTest(tool_type=string_value):
                tool_usage = ToolUsage(
                    tool_name="test_tool",
                    tool_type=string_value,
                    log_file="test.log"
                )
                
                self.assertEqual(tool_usage.tool_type, expected_enum)


class TestCodexRunResultErrorHandling(unittest.TestCase):
    """Test error handling in CodexRunResult properties and methods."""
    
    def test_duration_with_none_end_time(self):
        """Test duration property returns None when end_time is None."""
        run_result = CodexRunResult(
            run_id="test_run",
            start_time=datetime.now(),
            end_time=None  # No end time
        )
        
        self.assertIsNone(run_result.duration)
    
    def test_files_modified_with_none_values(self):
        """Test files_modified handles None file paths gracefully."""
        # Create changes and patches with None file paths
        change_with_none = CodexChange(
            type=ChangeType.PATCH,
            log_file="test.log",
            content="test",
            file_path=None
        )
        
        patch_data = PatchData(
            file_path="test.py",
            diff_content="diff",
            log_file="test.log"
        )
        
        tool_with_none = ToolUsage(
            tool_name="test_tool",
            tool_type=ToolType.EDIT,
            log_file="test.log",
            target_file=None
        )
        
        run_result = CodexRunResult(
            run_id="test_run",
            start_time=datetime.now(),
            changes=[change_with_none],
            patches=[patch_data],
            tool_usage=[tool_with_none]
        )
        
        # Should only include non-None file paths
        files = run_result.files_modified
        self.assertEqual(files, ["test.py"])
    
    def test_get_changes_by_type_error_handling(self):
        """Test get_changes_by_type handles errors gracefully."""
        run_result = CodexRunResult(
            run_id="test_run",
            start_time=datetime.now(),
            changes=[]
        )
        
        # Should handle empty changes list
        result = run_result.get_changes_by_type(ChangeType.PATCH)
        self.assertEqual(result, [])

    def test_duration_with_valid_end_time(self):
        """Test duration property calculates correctly when end_time is set."""
        start = datetime(2024, 1, 1, 10, 0, 0)
        end = datetime(2024, 1, 1, 10, 0, 5)  # 5 seconds later
        
        run_result = CodexRunResult(
            run_id="test_run",
            start_time=start,
            end_time=end
        )
        
        self.assertEqual(run_result.duration, 5.0)
    
    def test_get_tools_by_type_error_handling(self):
        """Test get_tools_by_type handles errors gracefully."""
        run_result = CodexRunResult(
            run_id="test_run",
            start_time=datetime.now(),
            tool_usage=[]
        )
        
        # Should handle empty tool usage list
        result = run_result.get_tools_by_type(ToolType.EDIT)
        self.assertEqual(result, [])

    def test_duration_with_valid_end_time(self):
        """Test duration property calculates correctly when end_time is set."""
        start = datetime(2024, 1, 1, 10, 0, 0)
        end = datetime(2024, 1, 1, 10, 0, 5)  # 5 seconds later
        
        run_result = CodexRunResult(
            run_id="test_run",
            start_time=start,
            end_time=end
        )
        
        self.assertEqual(run_result.duration, 5.0)

    def test_files_modified_comprehensive_coverage(self):
        """Test files_modified property with comprehensive coverage of all branches."""
        # Create objects that will test all conditional paths
        change_with_file = CodexChange(
            type=ChangeType.PATCH,
            log_file="test.log",
            content="test",
            file_path="change_file.py"
        )
        
        change_without_file = CodexChange(
            type=ChangeType.COMMAND,
            log_file="test.log", 
            content="test",
            file_path=None  # No file path
        )
        
        patch_data = PatchData(
            file_path="patch_file.py",
            diff_content="diff",
            log_file="test.log"
        )
        
        tool_with_file = ToolUsage(
            tool_name="test_tool",
            tool_type=ToolType.EDIT,
            log_file="test.log",
            target_file="tool_file.py"
        )
        
        tool_without_file = ToolUsage(
            tool_name="test_tool2",
            tool_type=ToolType.READ,
            log_file="test.log",
            target_file=None  # No target file
        )
        
        run_result = CodexRunResult(
            run_id="test_run",
            start_time=datetime.now(),
            changes=[change_with_file, change_without_file],
            patches=[patch_data],
            tool_usage=[tool_with_file, tool_without_file]
        )
        
        files = run_result.files_modified
        expected_files = ["change_file.py", "patch_file.py", "tool_file.py"]
        self.assertEqual(sorted(files), expected_files)


class TestCodexSessionResultErrorHandling(unittest.TestCase):
    """Test error handling in CodexSessionResult properties."""
    
    def test_total_files_modified_with_empty_runs(self):
        """Test total_files_modified handles empty runs list."""
        session_result = CodexSessionResult(
            session_id="test_session",
            runs=[]  # Empty runs
        )
        
        self.assertEqual(session_result.total_files_modified, [])
    
    def test_total_changes_with_empty_runs(self):
        """Test total_changes handles empty runs list."""
        session_result = CodexSessionResult(
            session_id="test_session",
            runs=[]
        )
        
        self.assertEqual(session_result.total_changes, 0)
    
    def test_successful_runs_filtering(self):
        """Test successful_runs filters correctly."""
        # Create successful and failed runs
        successful_run = CodexRunResult(
            run_id="success",
            start_time=datetime.now(),
            success=True
        )
        
        failed_run = CodexRunResult(
            run_id="failure",
            start_time=datetime.now(),
            success=False
        )
        
        session_result = CodexSessionResult(
            session_id="test_session",
            runs=[successful_run, failed_run]
        )
        
        successful = session_result.successful_runs
        self.assertEqual(len(successful), 1)
        self.assertEqual(successful[0].run_id, "success")
    
    def test_get_runs_by_file_with_no_matches(self):
        """Test get_runs_by_file when no runs match the file."""
        run_result = CodexRunResult(
            run_id="test_run",
            start_time=datetime.now()
        )
        
        session_result = CodexSessionResult(
            session_id="test_session",
            runs=[run_result]
        )
        
        # Should return empty list for non-existent file
        result = session_result.get_runs_by_file("nonexistent.py")
        self.assertEqual(result, [])

    def test_session_result_with_mixed_run_states(self):
        """Test CodexSessionResult properties with mixed None and valid runs."""
        # Create a mix of None and valid runs to test the conditional branches
        valid_run = CodexRunResult(
            run_id="valid_run",
            start_time=datetime.now(),
            success=True,
            changes=[
                CodexChange(
                    type=ChangeType.PATCH,
                    log_file="test.log",
                    content="test",
                    file_path="test.py"
                )
            ]
        )
        
        session_result = CodexSessionResult(
            session_id="mixed_session",
            runs=[valid_run, None, valid_run]  # Mix of valid and None runs
        )
        
        # Test total_files_modified with None runs
        files = session_result.total_files_modified
        self.assertEqual(files, ["test.py"])
        
        # Test total_changes with None runs  
        total_changes = session_result.total_changes
        self.assertEqual(total_changes, 2)  # Only from valid runs
        
        # Test successful_runs filtering
        successful = session_result.successful_runs
        self.assertEqual(len(successful), 2)
        
        # Test get_runs_by_file with None runs
        runs_for_file = session_result.get_runs_by_file("test.py")
        self.assertEqual(len(runs_for_file), 2)


class TestDiscoveredToolErrorHandling(unittest.TestCase):
    """Test error handling in DiscoveredTool."""
    
    def test_discovered_tool_with_none_values(self):
        """Test DiscoveredTool handles None values gracefully."""
        tool = DiscoveredTool(
            tool_name=None,  # None tool name
            invocation=None,  # None invocation
            type="shell",
            log_file="test.log"
        )
        
        # Should not crash during initialization
        self.assertIsNone(tool.tool_name)
        self.assertIsNone(tool.invocation)
    
    def test_discovered_tool_with_empty_strings(self):
        """Test DiscoveredTool handles empty strings."""
        tool = DiscoveredTool(
            tool_name="",  # Empty string
            invocation="",  # Empty string
            type="shell",
            log_file=""  # Empty log file
        )
        
        # Should handle gracefully
        self.assertEqual(tool.tool_name, "")
        self.assertEqual(tool.invocation, "")
        self.assertEqual(tool.log_file, "")


class TestEnumErrorHandling(unittest.TestCase):
    """Test error handling in enum usage."""
    
    def test_change_type_enum_values(self):
        """Test ChangeType enum has expected values."""
        self.assertEqual(ChangeType.PATCH.value, "patch")
        self.assertEqual(ChangeType.COMMAND.value, "command")
        self.assertEqual(ChangeType.TOOL_USE.value, "tool_use")
        self.assertEqual(ChangeType.CHANGES_DETECTED.value, "changes_detected")
        self.assertEqual(ChangeType.CUSTOM.value, "custom")
    
    def test_tool_type_enum_values(self):
        """Test ToolType enum has expected values."""
        self.assertEqual(ToolType.EDIT.value, "edit")
        self.assertEqual(ToolType.READ.value, "read")
        self.assertEqual(ToolType.SEARCH.value, "search")
        self.assertEqual(ToolType.LIST.value, "list")
        self.assertEqual(ToolType.DELETE.value, "delete")
        self.assertEqual(ToolType.RUN.value, "run")
        self.assertEqual(ToolType.CREATE.value, "create")
        self.assertEqual(ToolType.WEB.value, "web")
        self.assertEqual(ToolType.UNKNOWN.value, "unknown")


if __name__ == '__main__':
    unittest.main() 