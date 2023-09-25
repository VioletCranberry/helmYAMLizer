# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module

import os
import unittest
from unittest.mock import patch
from helmYAMLizer import ensure_dirs_exists
from .utils import check_expected_logging_call


class TestEnsureDirsExists(unittest.TestCase):
    """'ensure_dirs_exists' function test cases."""

    @patch("os.path.exists", return_value=False)
    @patch("os.makedirs")
    # pylint: disable=unused-argument
    def test_creates_directory(self, mock_makedirs, mock_exist):
        """Test that directories are created if they don't exist."""
        path = "/testpath/filename.txt"
        ensure_dirs_exists(path)
        mock_makedirs.assert_called_once_with(os.path.dirname(path), exist_ok=True)

    def test_empty_folder_path(self):
        """Test that the function exits early for a filename without a directory."""
        path = "filename.txt"
        # No exception should be raised in this case.
        ensure_dirs_exists(path)

    @patch("os.path.exists", return_value=True)
    @patch("os.makedirs")
    # pylint: disable=unused-argument
    def test_does_not_create_existing_directory(self, mock_makedirs, mock_exist):
        """Test that directories are not created if they already exist."""
        path = "/testpath/filename.txt"
        ensure_dirs_exists(path)
        mock_makedirs.assert_not_called()

    @patch("helmYAMLizer.sys.exit")
    @patch("helmYAMLizer.logging.fatal")
    def test_non_string_input(self, mock_logging, mock_exit):
        """Test that a ValueError is raised for non-string inputs."""
        ensure_dirs_exists(12345)
        # Check if the expected logging call was made.
        error_msg = "Provided path must be a string."
        self.assertTrue(
            check_expected_logging_call(
                mock_logging, "ensure_dirs_exists", ValueError, error_msg
            ),
            "Expected logging call not found.",
        )
        # Ensure sys.exit(1) was called.
        mock_exit.assert_called_once_with(1)

    @patch("os.path.exists", return_value=False)
    @patch("os.makedirs", side_effect=OSError("Mock error"))
    @patch("helmYAMLizer.sys.exit")
    @patch("helmYAMLizer.logging.fatal")
    # pylint: disable=unused-argument
    def test_os_error_raised(self, mock_logging, mock_exit, mock_makedirs, mock_exists):
        """Test that a RuntimeError is raised if os.makedirs throws an OSError."""
        path = "/testpath/filename.txt"
        ensure_dirs_exists(path)
        # Check if `os.makedirs` was called.
        mock_makedirs.assert_called_once()
        # Check if the expected logging call was made.
        error_msg = "Failed to create directory '/testpath'. Error: Mock error"
        self.assertTrue(
            check_expected_logging_call(
                mock_logging, "ensure_dirs_exists", RuntimeError, error_msg
            ),
            "Expected logging call not found.",
        )
        # Ensure sys.exit(1) was called due to the error.
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
