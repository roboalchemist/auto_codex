import unittest
import os
import shutil
from auto_codex.parsers import CodexLogParser
from auto_codex.models import ChangeType

class TestLogParsing(unittest.TestCase):

    def setUp(self):
        self.test_dir = 'tests/test_data/log_files/'
        self.log_file = os.path.join(self.test_dir, 'Two_Sum.log')

    def test_parse_two_sum_log(self):
        parser = CodexLogParser(self.test_dir)
        run_result = parser.parse_run(self.log_file)
        
        self.assertEqual(len(run_result.patches), 1)
        patch = run_result.patches[0]
        self.assertEqual(patch.file_path, 'two_sum.py')
        self.assertIn('def two_sum', patch.diff_content)
        
        self.assertEqual(len(run_result.commands), 1)
        command = run_result.commands[0]
        self.assertEqual(command.tool_name, 'shell')
        
        # Check that the arguments contain apply_patch
        args = command.arguments
        if isinstance(args, dict) and "command" in args:
            self.assertIn('apply_patch', args["command"][0])
        elif isinstance(args, str):
            self.assertIn('apply_patch', args)

    def test_find_log_files(self):
        parser = CodexLogParser(self.test_dir, log_pattern="*.log")
        log_files = parser.get_log_files()
        self.assertGreater(len(log_files), 0)
        self.assertIn(self.log_file, log_files)

if __name__ == '__main__':
    unittest.main() 