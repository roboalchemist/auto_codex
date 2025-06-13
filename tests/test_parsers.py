import unittest
import os
import shutil
from auto_codex.parsers import CodexLogParser, CodexOutputParser
from auto_codex.models import ChangeType

class TestParsers(unittest.TestCase):

    def setUp(self):
        self.test_dir = 'auto_codex/tests/'
        self.log_pattern = "parser_test_data_*.log"
        self.log_file_1 = os.path.join(self.test_dir, 'parser_test_data_1.log')
        self.log_file_2 = os.path.join(self.test_dir, 'parser_test_data_2.log')

    def test_find_log_files(self):
        parser = CodexLogParser(self.test_dir, log_pattern=self.log_pattern)
        log_files = parser.get_log_files()
        self.assertEqual(len(log_files), 2)
        self.assertIn(self.log_file_1, log_files)
        self.assertIn(self.log_file_2, log_files)

    def test_parse_run(self):
        parser = CodexLogParser(self.test_dir, log_pattern=self.log_pattern)
        run_result = parser.parse_run(self.log_file_2)
        self.assertEqual(len(run_result.patches), 0)  # No patches in this log file
        self.assertEqual(len(run_result.commands), 9)  # 9 shell commands found

    def test_discover_tools(self):
        parser = CodexLogParser(self.test_dir, log_pattern=self.log_pattern)
        tools = parser.discover_tools()
        self.assertIn('shell', tools)
        self.assertEqual(tools['shell']['count'], 9)  # 9 shell commands found

    def test_filter_by_file_extension(self):
        parser = CodexLogParser(self.test_dir, log_pattern=self.log_pattern)
        changes = parser.parse_logs()
        py_changes = parser.filter_by_file_extension(changes, '.py')
        self.assertEqual(len(py_changes), 0)  # No .py file changes in test data
        # Test that we can filter changes (even if result is empty)
        self.assertIsInstance(py_changes, list)

    def test_output_parser_diff(self):
        output_parser = CodexOutputParser()
        diff_content = """
        --- a/file.py
        +++ b/file.py
        @@ -1,3 +1,4 @@
         line 1
         line 2
        +new line
         line 3
        """
        parsed = output_parser.parse_diff(diff_content)
        self.assertEqual(parsed['added'], 1)
        self.assertEqual(parsed['removed'], 0)

    def test_output_parser_command(self):
        output_parser = CodexOutputParser()
        command_output = "stdout: some output\nstderr: an error"
        parsed = output_parser.parse_command_output(command_output)
        self.assertEqual(parsed['stdout'], 'some output')
        self.assertEqual(parsed['stderr'], 'an error')

    def tearDown(self):
        # The test data files are permanent, but we could clean up
        # other files created during tests here if needed.
        pass

if __name__ == '__main__':
    unittest.main() 