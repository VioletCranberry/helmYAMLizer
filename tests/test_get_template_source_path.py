# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module

import unittest
from unittest.mock import patch
from helmYAMLizer import get_template_source_path
from .utils import check_expected_logging_call


class TestGetTemplateSourcePath(unittest.TestCase):
    """'get_template_source_path' function test cases."""

    def test_valid_comment(self):
        """Test that a valid comment returns the correct source path."""
        comment = "# Source: some/path.yaml"
        expected = "some/path.yaml"
        with patch("helmYAMLizer.logging.debug") as mock_debug:
            result = get_template_source_path(comment)
            mock_debug.assert_called_with("Document source path: %s", expected)
            self.assertEqual(result, expected)

    @patch("helmYAMLizer.sys.exit")
    @patch("helmYAMLizer.logging.fatal")
    def test_invalid_prefix(self, mock_logging, mock_exit):
        """Test that a comment with an invalid prefix raises a ValueError."""
        comment = "# NotSource: some/path.yaml"
        get_template_source_path(comment)
        # Check if the expected logging call was made.
        error_msg = "Comment # NotSource: some/path.yaml does not begin with # Source:"
        self.assertTrue(
            check_expected_logging_call(
                mock_logging, "get_template_source_path", ValueError, error_msg
            ),
            "Expected logging call not found.",
        )
        # Ensure sys.exit(1) was called.
        mock_exit.assert_called_once_with(1)

    @patch("helmYAMLizer.sys.exit")
    @patch("helmYAMLizer.logging.fatal")
    def test_non_string_input(self, mock_logging, mock_exit):
        """Test that a non-string input raises a ValueError."""
        get_template_source_path(12345)
        # Check if the expected logging call was made.
        error_msg = "Expected a string for comment, but got <class 'int'>."
        self.assertTrue(
            check_expected_logging_call(
                mock_logging, "get_template_source_path", ValueError, error_msg
            ),
            "Expected logging call not found.",
        )
        # Ensure sys.exit(1) was called.
        mock_exit.assert_called_once_with(1)

    @patch("helmYAMLizer.sys.exit")
    @patch("helmYAMLizer.logging.fatal")
    def test_malformed_comment(self, mock_logging, mock_exit):
        """Test that a malformed comment raises a ValueError."""
        comment = "# Source:"
        get_template_source_path(comment)
        error_msg = (
            "Comment '# Source:' is malformed and cannot be split appropriately."
        )
        self.assertTrue(
            check_expected_logging_call(
                mock_logging, "get_template_source_path", ValueError, error_msg
            ),
            "Expected logging call not found.",
        )
        # Ensure sys.exit(1) was called.
        mock_exit.assert_called_once_with(1)

    @patch("helmYAMLizer.sys.exit")
    @patch("helmYAMLizer.logging.fatal")
    def test_comment_without_path(self, mock_logging, mock_exit):
        """Test that a comment without path raises a ValueError."""
        comment = "# Source: "
        get_template_source_path(comment)
        error_msg = "Comment '# Source: ' is missing a template path after '# Source:'."
        self.assertTrue(
            check_expected_logging_call(
                mock_logging, "get_template_source_path", ValueError, error_msg
            ),
            "Expected logging call not found.",
        )
        # Ensure sys.exit(1) was called.
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
