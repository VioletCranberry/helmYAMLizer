# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module

import unittest
from unittest.mock import patch
from helmYAMLizer import flatten_source_path
from .utils import check_expected_logging_call


class TestFlattenSourcePath(unittest.TestCase):
    """'flatten_source_path' function test cases."""

    def test_path_starts_with_crds(self):
        """Test that paths starting with 'crds/' are returned unchanged."""
        test_path = "crds/some_path.yaml"
        self.assertEqual(flatten_source_path(test_path), test_path)

    def test_path_contains_templates(self):
        """Test that paths containing '/templates/' return the part after '/templates/'."""
        test_path = "some_dir/templates/some_path.yaml"
        expected = "some_path.yaml"
        self.assertEqual(flatten_source_path(test_path), expected)

    @patch("helmYAMLizer.sys.exit")
    @patch("helmYAMLizer.logging.fatal")
    def test_invalid_path(self, mock_logging, mock_exit):
        """Test that a path not meeting conditions raises a ValueError."""
        test_path = "some_dir/some_path.yaml"
        flatten_source_path(test_path)
        # Check if the expected logging call was made.
        error_msg = (
            "The path 'some_dir/some_path.yaml' neither starts "
            "with 'crds/' nor contains '/templates/'."
        )
        self.assertTrue(
            check_expected_logging_call(
                mock_logging, "flatten_source_path", ValueError, error_msg
            ),
            "Expected logging call not found.",
        )
        # Check if sys.exit(1) was called.
        mock_exit.assert_called_once_with(1)

    @patch("helmYAMLizer.sys.exit")
    @patch("helmYAMLizer.logging.fatal")
    def test_non_string_input(self, mock_logging, mock_exit):
        """Test that a non-string input raises a ValueError."""
        flatten_source_path(12345)
        # Check if the expected logging call was made.
        error_msg = "Expected a string for template path, but got <class 'int'>."
        self.assertTrue(
            check_expected_logging_call(
                mock_logging, "flatten_source_path", ValueError, error_msg
            ),
            "Expected logging call not found.",
        )
        # Check if sys.exit(1) was called.
        mock_exit.assert_called_once_with(1)
