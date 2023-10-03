# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module

import unittest
from unittest.mock import patch
from helmYAMLizer import drop_label_keys
from .utils import check_expected_logging_call


class TestDropLabelKeys(unittest.TestCase):
    """'drop_label_keys' function test cases."""

    def test_basic_case(self):
        """Testing a basic dictionary structure with some labels to drop."""
        data = {
            "name": "test",
            "labels": {"a": "value_a", "b": "value_b"},
            "details": "Some details",
        }
        label_keys = ["a"]
        expected = {
            "name": "test",
            "labels": {"b": "value_b"},
            "details": "Some details",
        }
        self.assertEqual(drop_label_keys(data, label_keys), expected)

    def test_recursive_case(self):
        """Testing a dictionary that has nested dictionaries containing labels."""
        data = {
            "name": "test",
            "labels": {"a": "value_a", "b": "value_b"},
            "details": {"labels": {"a": "value_a_nested", "c": "value_c"}},
        }
        label_keys = ["a"]
        expected = {
            "name": "test",
            "labels": {"b": "value_b"},
            "details": {"labels": {"c": "value_c"}},
        }
        self.assertEqual(drop_label_keys(data, label_keys), expected)

    def test_list_case(self):
        """Testing a dictionary that contains a list of dictionaries with labels."""
        data = {
            "name": "test",
            "items": [
                {"labels": {"a": "value_a", "b": "value_b"}},
                {"labels": {"a": "value_a_nested", "c": "value_c"}},
            ],
        }
        label_keys = ["a"]
        expected = {
            "name": "test",
            "items": [{"labels": {"b": "value_b"}}, {"labels": {"c": "value_c"}}],
        }
        self.assertEqual(drop_label_keys(data, label_keys), expected)

    @patch("helmYAMLizer.sys.exit")
    @patch("helmYAMLizer.logging.fatal")
    def test_invalid_label_keys(self, mock_logging, mock_exit):
        """Testing with invalid label keys (not all are strings)."""
        data = {"name": "test"}
        label_keys = ["a", 123]
        drop_label_keys(data, label_keys)
        error_msg = "label_keys must be a list of strings."
        self.assertTrue(
            check_expected_logging_call(
                mock_logging, "drop_label_keys", ValueError, error_msg
            ),
            "Expected logging call not found.",
        )
        # Check if sys.exit(1) was called.
        mock_exit.assert_called_once_with(1)

    def test_non_dict_or_list_data(self):
        """Testing with a data type that is neither dictionary nor list."""
        data = "Some string data"
        label_keys = ["a"]
        self.assertEqual(drop_label_keys(data, label_keys), data)
