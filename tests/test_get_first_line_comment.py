# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module

import unittest
from unittest.mock import patch, Mock
from helmYAMLizer import get_first_line_comment


class TestGetFirstLineComment(unittest.TestCase):
    """'get_first_line_comment' function test cases."""

    @patch("helmYAMLizer.logging.debug")
    def test_document_is_none(self, mock_logging):
        """Test that the function returns None when the document is None."""
        self.assertIsNone(get_first_line_comment(None))
        mock_logging.assert_not_called()

    @patch("helmYAMLizer.logging.debug")
    def test_document_not_a_dictionary(self, mock_logging):
        """Test that the function returns None when the document is not a dictionary."""
        self.assertIsNone(get_first_line_comment(["list_item"]))
        mock_logging.assert_not_called()

    @patch("helmYAMLizer.logging.debug")
    def test_document_with_no_comment(self, mock_logging):
        """Test that the function returns None when the document does not have a comment."""
        document = {}
        self.assertIsNone(get_first_line_comment(document))
        mock_logging.assert_not_called()

    @patch("helmYAMLizer.logging.debug")
    def test_document_with_comment(self, mock_logging):
        """
        Test that the function retrieves the comment from the first line
         of the YAML document if it exists.
        """
        document = Mock(spec=dict)
        document.ca = Mock()
        comment_token = Mock()
        comment_token.value = " # This is a comment "
        document.ca.comment = [None, [comment_token]]
        self.assertEqual(get_first_line_comment(document), "# This is a comment")
        mock_logging.assert_called_once()

    @patch("helmYAMLizer.logging.debug")
    def test_document_with_unexpected_structure(self, mock_logging):
        """
        Test that the function gracefully handles documents with
        unexpected structures and returns None.
        """
        document = Mock(spec=dict)
        document.ca = Mock()
        document.ca.comment = None
        self.assertIsNone(get_first_line_comment(document))
        mock_logging.assert_not_called()


if __name__ == "__main__":
    unittest.main()
