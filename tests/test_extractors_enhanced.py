import unittest
import tempfile
import os
import shutil
import json
import re
from auto_codex.extractors import (
    BaseExtractor, PatchExtractor, CommandExtractor, ToolUsageExtractor, 
    ChangeDetector, CustomExtractor, GenericToolExtractor
)
from auto_codex.models import (
    PatchData, CodexCommand, ToolUsage, CodexChange, DiscoveredTool,
    ChangeType, ToolType
)
from unittest.mock import patch, MagicMock


class TestBaseExtractor(unittest.TestCase):
    """Test the BaseExtractor base class."""

    def test_base_extractor_not_implemented(self):
        """Test that BaseExtractor raises NotImplementedError."""
        extractor = BaseExtractor()
        with self.assertRaises(NotImplementedError):
            extractor.extract("test.log", "content")

    def test_matches_file_pattern_no_pattern(self):
        """Test file pattern matching when no pattern is set."""
        extractor = BaseExtractor()
        self.assertTrue(extractor._matches_file_pattern("any_file.py"))
        self.assertTrue(extractor._matches_file_pattern("another_file.txt"))

    def test_matches_file_pattern_with_pattern(self):
        """Test file pattern matching with regex pattern."""
        import re
        extractor = BaseExtractor(file_pattern=r"\.py$")
        extractor.file_pattern = re.compile(r"\.py$")
        
        self.assertTrue(extractor._matches_file_pattern("script.py"))
        self.assertFalse(extractor._matches_file_pattern("document.txt"))


class TestPatchExtractorEdgeCases(unittest.TestCase):
    """Test edge cases in PatchExtractor."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_patch_extractor_malformed_json(self):
        """Test handling of malformed JSON in log content."""
        extractor = PatchExtractor()
        content = """
{invalid json
{"name": "shell", but missing closing brace
"""
        results = extractor.extract(self.log_file, content)
        self.assertEqual(len(results), 0)

    def test_patch_extractor_no_shell_commands(self):
        """Test extraction when there are no shell commands."""
        extractor = PatchExtractor()
        content = """
{"name": "other_tool", "arguments": "{}"}
{"name": "read_file", "arguments": "{}"}
"""
        results = extractor.extract(self.log_file, content)
        self.assertEqual(len(results), 0)

    def test_patch_extractor_shell_without_apply_patch(self):
        """Test shell commands that are not apply_patch."""
        extractor = PatchExtractor()
        log_content = json.dumps({
            "name": "shell",
            "arguments": json.dumps({"command": ["ls", "-la"]})
        })
        
        results = extractor.extract(self.log_file, log_content)
        self.assertEqual(len(results), 0)

    def test_patch_extractor_empty_command_list(self):
        """Test handling of empty command list."""
        extractor = PatchExtractor()
        log_content = json.dumps({
            "name": "shell",
            "arguments": json.dumps({"command": []})
        })
        
        results = extractor.extract(self.log_file, log_content)
        self.assertEqual(len(results), 0)

    def test_patch_extractor_invalid_arguments_json(self):
        """Test handling of invalid arguments JSON."""
        extractor = PatchExtractor()
        log_content = json.dumps({
            "name": "shell",
            "arguments": "invalid json"
        })
        
        results = extractor.extract(self.log_file, log_content)
        self.assertEqual(len(results), 0)

    def test_patch_extractor_with_file_pattern(self):
        """Test patch extractor with file pattern filter."""
        import re
        extractor = PatchExtractor(file_pattern=r"\.py$")
        extractor.file_pattern = re.compile(r"\.py$")
        
        patch_content = "*** Begin Patch\n*** Update File: script.py\n@@ -1,3 +1,5 @@\n+def new_function():\n+    pass\n*** End Patch"
        log_content = json.dumps({
            "type": "function_call_output",
            "call_id": "call_123",
            "name": "shell",
            "arguments": json.dumps({"command": ["apply_patch", patch_content]})
        })
        
        # Write to the log file to test actual extraction
        with open(self.log_file, 'w') as f:
            f.write(log_content)
            
        results = extractor.extract(self.log_file, log_content)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].file_path, "script.py")

    def test_patch_extractor_file_pattern_no_match(self):
        """Test patch extractor where file doesn't match pattern."""
        import re
        extractor = PatchExtractor(file_pattern=r"\.py$")
        extractor.file_pattern = re.compile(r"\.py$")
        
        patch_content = "Update File: document.txt @@...@@ some diff content *** End Patch"
        log_content = json.dumps({
            "name": "shell",
            "arguments": json.dumps({"command": ["apply_patch", patch_content]})
        })
        
        results = extractor.extract(self.log_file, log_content)
        self.assertEqual(len(results), 0)


class TestCommandExtractorEdgeCases(unittest.TestCase):
    """Test edge cases in CommandExtractor."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_command_extractor_no_arguments(self):
        """Test handling of command without arguments."""
        extractor = CommandExtractor()
        content = """{"name": "shell", "tool_call": true}"""
        
        results = extractor.extract(self.log_file, content)
        self.assertEqual(len(results), 0)

    def test_command_extractor_arguments_as_object(self):
        """Test handling of arguments as object rather than string."""
        extractor = CommandExtractor()
        log_content = json.dumps({
            "name": "shell",
            "function_call": True,
            "arguments": {"command": "ls -la", "target_file": "script.py"}
        })
        
        results = extractor.extract(self.log_file, log_content)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].command, "ls -la")
        self.assertEqual(results[0].target_files, ["script.py"])

    def test_command_extractor_json_decode_error_in_args(self):
        """Test handling of JSON decode error in arguments."""
        extractor = CommandExtractor()
        log_content = json.dumps({
            "name": "shell",
            "tool_use": True,
            "arguments": "invalid json string"
        })
        
        results = extractor.extract(self.log_file, log_content)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].arguments, "invalid json string")

    def test_command_extractor_multiple_target_files(self):
        """Test extraction of multiple target file arguments."""
        extractor = CommandExtractor()
        log_content = json.dumps({
            "name": "file_manager",
            "function_call": True,
            "arguments": {
                "command": "copy_files",
                "target_file": "file1.py",
                "file_path": "file2.py",
                "filename": "file3.py",
                "path": "file4.py"
            }
        })
        
        results = extractor.extract(self.log_file, log_content)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0].target_files), 4)
        self.assertIn("file1.py", results[0].target_files)
        self.assertIn("file2.py", results[0].target_files)

    def test_command_extractor_non_dict_arguments(self):
        """Test handling of non-dict arguments."""
        extractor = CommandExtractor()
        log_content = json.dumps({
            "name": "tool",
            "tool_call": True,
            "arguments": ["list", "of", "args"]
        })
        
        results = extractor.extract(self.log_file, log_content)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].command, "['list', 'of', 'args']")


class TestToolUsageExtractorEdgeCases(unittest.TestCase):
    """Test edge cases in ToolUsageExtractor."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_tool_usage_extractor_no_tool_name(self):
        """Test handling of tool call without name."""
        extractor = ToolUsageExtractor()
        log_content = json.dumps({
            "function_call": True,
            "arguments": {"command": "test"}
        })
        
        results = extractor.extract(self.log_file, log_content)
        self.assertEqual(len(results), 0)

    def test_tool_usage_extractor_invalid_args_json(self):
        """Test handling of invalid arguments JSON."""
        extractor = ToolUsageExtractor()
        log_content = json.dumps({
            "name": "shell",
            "tool_use": True,
            "arguments": "invalid json"
        })
        
        results = extractor.extract(self.log_file, log_content)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].arguments, {})

    def test_categorize_tool_all_types(self):
        """Test tool categorization for all tool types."""
        extractor = ToolUsageExtractor()
        
        test_cases = [
            ("edit_file", ToolType.EDIT),
            ("file_writer", ToolType.EDIT),
            ("read_file", ToolType.READ),
            ("cat_command", ToolType.READ),
            ("search_files", ToolType.SEARCH),
            ("grep_tool", ToolType.SEARCH),
            ("list_directory", ToolType.LIST),
            ("ls_command", ToolType.LIST),
            ("delete_file", ToolType.DELETE),
            ("remove_tool", ToolType.DELETE),
            ("run_command", ToolType.RUN),
            ("terminal_exec", ToolType.DELETE),
            ("create_file", ToolType.CREATE),
            ("make_directory", ToolType.LIST),
            ("web_search", ToolType.SEARCH),
            ("browser_tool", ToolType.WEB),
            ("unknown_tool", ToolType.UNKNOWN)
        ]
        
        for tool_name, expected_type in test_cases:
            with self.subTest(tool_name=tool_name):
                result = extractor._categorize_tool(tool_name)
                self.assertEqual(result, expected_type)

    def test_tool_usage_target_file_extraction(self):
        """Test target file extraction from various argument keys."""
        extractor = ToolUsageExtractor()
        
        test_cases = [
            ({"target_file": "file1.py"}, "file1.py"),
            ({"file_path": "file2.py"}, "file2.py"),
            ({"filename": "file3.py"}, "file3.py"),
            ({"path": "file4.py"}, "file4.py"),
            ({"other_key": "file5.py"}, None),
            ({}, None)
        ]
        
        for args, expected_file in test_cases:
            with self.subTest(args=args):
                log_content = json.dumps({
                    "name": "test_tool",
                    "function_call": True,
                    "arguments": args
                })
                
                results = extractor.extract(self.log_file, log_content)
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0].target_file, expected_file)


class TestChangeDetector(unittest.TestCase):
    """Test ChangeDetector extractor."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_change_detector_valid_change(self):
        """Test detection of valid change entries."""
        extractor = ChangeDetector()
        log_content = json.dumps({
            "type": "codex_change",
            "change_type": "patch",
            "file_path": "script.py",
            "content": "some change content"
        })
        
        results = extractor.extract(self.log_file, log_content)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].type, ChangeType.PATCH)
        self.assertEqual(results[0].file_path, "script.py")

    def test_change_detector_invalid_change_type(self):
        """Test handling of invalid change type."""
        extractor = ChangeDetector()
        log_content = json.dumps({
            "type": "codex_change",
            "change_type": "INVALID_TYPE",
            "file_path": "script.py"
        })
        
        results = extractor.extract(self.log_file, log_content)
        self.assertEqual(len(results), 0)

    def test_change_detector_missing_file_path(self):
        """Test handling of missing file path."""
        extractor = ChangeDetector()
        log_content = json.dumps({
            "type": "codex_change",
            "change_type": "PATCH"
        })
        
        results = extractor.extract(self.log_file, log_content)
        self.assertEqual(len(results), 0)

    def test_change_detector_with_file_pattern(self):
        """Test change detector with file pattern filter."""
        import re
        extractor = ChangeDetector(file_pattern=r"\.py$")
        extractor.file_pattern = re.compile(r"\.py$")
        
        content = f"""
{json.dumps({"type": "codex_change", "change_type": "patch", "file_path": "script.py"})}
{json.dumps({"type": "codex_change", "change_type": "patch", "file_path": "document.txt"})}
"""
        
        results = extractor.extract(self.log_file, content)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].file_path, "script.py")


class TestCustomExtractor(unittest.TestCase):
    """Test CustomExtractor functionality."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_custom_extractor_basic_pattern(self):
        """Test custom extractor with basic regex pattern."""
        extractor = CustomExtractor(pattern=r"ERROR: (.+)")
        content = "INFO: Starting process\nERROR: Something went wrong\nDEBUG: Continuing"
        
        results = extractor.extract(self.log_file, content)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].type, ChangeType.CUSTOM)
        self.assertIn("ERROR: Something went wrong", results[0].content)

    def test_custom_extractor_with_custom_change_type(self):
        """Test custom extractor with custom change type."""
        extractor = CustomExtractor(pattern=r"WARNING: (.+)", change_type="custom")
        content = "WARNING: This is a warning message"
        
        results = extractor.extract(self.log_file, content)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].type, ChangeType.CUSTOM)

    def test_custom_extractor_multiple_matches(self):
        """Test custom extractor finding multiple matches."""
        extractor = CustomExtractor(pattern=r"MATCH: [^\n]+")
        content = "MATCH: First match\nOther content\nMATCH: Second match"
        
        results = extractor.extract(self.log_file, content)
        self.assertEqual(len(results), 2)

    def test_custom_extractor_with_groups(self):
        """Test custom extractor capturing groups."""
        extractor = CustomExtractor(pattern=r"FILE: (\w+\.py) STATUS: (\w+)")
        content = "FILE: script.py STATUS: modified\nFILE: test.py STATUS: created"
        
        results = extractor.extract(self.log_file, content)
        self.assertEqual(len(results), 2)
        # Check that groups are captured in raw_match
        self.assertEqual(results[0].raw_match, ("script.py", "modified"))
        self.assertEqual(results[1].raw_match, ("test.py", "created"))

    def test_custom_extractor_no_groups(self):
        """Test custom extractor without capture groups."""
        extractor = CustomExtractor(pattern=r"SIMPLE MATCH")
        content = "SIMPLE MATCH found here"
        
        results = extractor.extract(self.log_file, content)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].raw_match, "SIMPLE MATCH")


class TestGenericToolExtractor(unittest.TestCase):
    """Test GenericToolExtractor functionality."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generic_tool_extractor_basic(self):
        """Test basic generic tool extraction."""
        extractor = GenericToolExtractor()
        log_content = json.dumps({
            "name": "shell",
            "function_call": True,
            "arguments": {"command": "ls"}
        })
        
        results = extractor.extract(self.log_file, log_content)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].tool_name, "shell")
        self.assertEqual(results[0].type, "function_call")

    def test_generic_tool_extractor_no_name(self):
        """Test handling of tool call without name."""
        extractor = GenericToolExtractor()
        log_content = json.dumps({
            "function_call": True,
            "arguments": {"command": "test"}
        })
        
        results = extractor.extract(self.log_file, log_content)
        self.assertEqual(len(results), 0)

    def test_generic_tool_extractor_multiple_keywords(self):
        """Test extraction with different tool call keywords."""
        extractor = GenericToolExtractor()
        content = f"""
{json.dumps({"name": "tool1", "function_call": True, "arguments": {}})}
{json.dumps({"name": "tool2", "tool_use": True, "arguments": {}})}
{json.dumps({"name": "tool3", "tool_call": True, "arguments": {}})}
"""
        
        results = extractor.extract(self.log_file, content)
        self.assertEqual(len(results), 3)
        tool_names = [r.tool_name for r in results]
        self.assertIn("tool1", tool_names)
        self.assertIn("tool2", tool_names)
        self.assertIn("tool3", tool_names)

    def test_generic_tool_extractor_json_error(self):
        """Test handling of JSON decode errors."""
        extractor = GenericToolExtractor()
        content = """
{"name": "valid_tool", "function_call": true, "arguments": {}}
{invalid json with function_call keyword
{"name": "another_tool", "tool_use": true, "arguments": {}}
"""
        
        results = extractor.extract(self.log_file, content)
        self.assertEqual(len(results), 2)


if __name__ == '__main__':
    unittest.main() 