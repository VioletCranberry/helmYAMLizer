# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module

import unittest
from unittest.mock import patch
from helmYAMLizer import prepare_file_path
from .utils import check_expected_logging_call


class TestPrepareFilePath(unittest.TestCase):
    """'prepare_file_path' function test cases."""

    @patch("helmYAMLizer.ensure_dirs_exists")
    @patch("os.path.join", return_value="/joined/path")
    def test_basic_functionality(self, mock_join, mock_ensure_dirs):
        """Test basic functionality of prepare_file_path."""
        result = prepare_file_path("target_dir", "flattened_path")
        mock_join.assert_called_once_with("target_dir", "flattened_path")
        mock_ensure_dirs.assert_called_once_with("/joined/path")
        self.assertEqual(result, "/joined/path")

    @patch("helmYAMLizer.sys.exit")
    @patch("helmYAMLizer.logging.fatal")
    def test_non_string_target_dir(self, mock_logging, mock_exit):
        """Test that a RunTimeError is raised for non-string target_dir."""
        prepare_file_path(12345, 12345)
        # Check if the expected logging call was made.
        error_msg = (
            "Failed to join file paths. Error: expected str, "
            "bytes or os.PathLike object, not int"
        )
        self.assertTrue(
            check_expected_logging_call(
                mock_logging, "prepare_file_path", RuntimeError, error_msg
            ),
            "Expected logging call not found.",
        )
        # Ensure sys.exit(1) was called.
        mock_exit.assert_called_once_with(1)
