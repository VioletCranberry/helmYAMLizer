# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module

import unittest
from unittest.mock import patch, mock_open
from ruamel.yaml import YAMLError
from helmYAMLizer import save_document_to_file
from .utils import check_expected_logging_call


class TestSaveDocumentToFile(unittest.TestCase):
    """'save_document_to_file' function test cases."""

    @patch("builtins.open", mock_open())
    @patch("helmYAMLizer.yaml.dump")
    def test_successful_save(self, mock_yaml_dump):
        """Test saving a document to a file successfully."""
        file_path = "testpath.yaml"
        document = {"key": "value"}
        save_document_to_file(file_path, document)
        mock_yaml_dump.assert_called_once_with(document, unittest.mock.ANY)

    @patch("helmYAMLizer.sys.exit")
    @patch("helmYAMLizer.logging.fatal")
    def test_non_dict_document(self, mock_logging, mock_exit):
        """Test failure when providing a non-dictionary as the document."""
        save_document_to_file("testpath.yaml", "not_a_dict")
        # Check if the expected logging call was made.
        error_msg = "Provided document must be a dictionary, but got <class 'str'>."
        self.assertTrue(
            check_expected_logging_call(
                mock_logging, "save_document_to_file", ValueError, error_msg
            ),
            "Expected logging call not found.",
        )
        # Ensure sys.exit(1) was called.
        mock_exit.assert_called_once_with(1)

    @patch("helmYAMLizer.sys.exit")
    @patch("helmYAMLizer.logging.fatal")
    def test_non_string_file_path(self, mock_logging, mock_exit):
        """Test failure when providing a non-string file path."""
        save_document_to_file([], {"key": "value"})
        # Check if the expected logging call was made.
        error_msg = "Provided file path must be a string, but got <class 'list'>."
        self.assertTrue(
            check_expected_logging_call(
                mock_logging, "save_document_to_file", ValueError, error_msg
            ),
            "Expected logging call not found.",
        )
        # Ensure sys.exit(1) was called.
        mock_exit.assert_called_once_with(1)

    @patch("helmYAMLizer.yaml.dump", side_effect=IOError("mock_io_error"))
    @patch("helmYAMLizer.sys.exit")
    @patch("helmYAMLizer.logging.fatal")
    @patch("builtins.open", mock_open())
    # pylint: disable=unused-argument
    def test_io_error(self, mock_logging, mock_exit, mock_yaml_dump):
        """Test failure due to IOError."""
        save_document_to_file("testpath.yaml", {"key": "value"})
        # Check if the expected logging call was made.
        error_msg = "Failed to save data to 'testpath.yaml'. IOError: mock_io_error"
        self.assertTrue(
            check_expected_logging_call(
                mock_logging, "save_document_to_file", RuntimeError, error_msg
            ),
            "Expected logging call not found.",
        )
        # Ensure sys.exit(1) was called.
        mock_exit.assert_called_once_with(1)

    @patch("helmYAMLizer.yaml.dump", side_effect=YAMLError("mock_yaml_error"))
    @patch("helmYAMLizer.sys.exit")
    @patch("helmYAMLizer.logging.fatal")
    @patch("builtins.open", mock_open())
    # pylint: disable=unused-argument
    def test_yaml_error(self, mock_logging, mock_exit, mock_yaml_dump):
        """Test failure due to YAMLError."""
        save_document_to_file("testpath.yaml", {"key": "value"})
        # Check if the expected logging call was made.
        error_msg = (
            "Failed to save data to 'testpath.yaml' due to YAML error: mock_yaml_error"
        )
        self.assertTrue(
            check_expected_logging_call(
                mock_logging, "save_document_to_file", RuntimeError, error_msg
            ),
            "Expected logging call not found.",
        )
        # Ensure sys.exit(1) was called.
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
