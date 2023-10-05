# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module

import unittest
from unittest.mock import patch, mock_open, ANY
from ruamel.yaml import CommentedMap

from helmYAMLizer import (
    collect_yaml_files,
    is_valid_yaml,
    create_kustom_data,
    save_kustom_data,
    generate_kustomize_file,
)


class TestKustomizeFileGenFunctions(unittest.TestCase):
    """Kustomize file generation functions tests."""

    @patch("os.walk")
    @patch("helmYAMLizer.is_valid_yaml")
    def test_collect_yaml_files(self, mock_is_valid, mock_walk):
        """
        Test the collect_yaml_files function to ensure it correctly identifies and
        collects YAML files from the given directory and its subdirectories.
        """
        # Simulate directory structure
        mock_walk.return_value = [
            ("/testdir", [], ["a.yaml", "b.yml", "c.txt", "kustomization.yaml"]),
        ]
        # Simulate valid YAML files determination
        mock_is_valid.side_effect = [True, True, False, False]
        result = collect_yaml_files("/testdir")
        self.assertEqual(result, ["a.yaml", "b.yml"])

    def test_is_valid_yaml(self):
        """
        Test the is_valid_yaml function to ensure it correctly identifies valid
        YAML filenames and excludes specified files.
        """
        self.assertTrue(is_valid_yaml("test.yaml"))
        self.assertTrue(is_valid_yaml("test.yml"))
        self.assertFalse(is_valid_yaml("test.txt"))
        self.assertFalse(is_valid_yaml("kustomization.yaml"))
        self.assertFalse(is_valid_yaml("kustomization.yml"))

    def test_create_kustom_data(self):
        """
        Test the create_kustom_data function to ensure it generates the correct
        kustomization data format based on the provided list of YAML files.
        """
        files = ["a.yaml", "b.yml"]
        result = create_kustom_data(files)
        self.assertEqual(result["apiVersion"], "kustomize.config.k8s.io/v1beta1")
        self.assertEqual(result["kind"], "Kustomization")
        self.assertEqual(result["resources"], files)

    @patch("helmYAMLizer.yaml.dump")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_kustom_data(self, mock_file, mock_dump):
        """
        Test the save_kustom_data function to ensure it correctly writes the
        provided kustomization data to a file in the specified directory.
        """
        kustom_data = CommentedMap({"key": "value"})
        directory = "/testdir"
        save_kustom_data(directory, kustom_data)
        # Check if the correct path was used for saving the data
        mock_file.assert_called_with(
            "/testdir/kustomization.yaml", encoding="utf-8", mode="w"
        )
        # Check if data dumping was called
        mock_dump.assert_called_once_with(kustom_data, ANY)

    @patch("helmYAMLizer.collect_yaml_files")
    @patch("helmYAMLizer.create_kustom_data")
    @patch("helmYAMLizer.save_kustom_data")
    def test_generate_kustomize_file(self, mock_save, mock_create, mock_collect):
        """
        Test the generate_kustomize_file function to ensure the whole workflow
        of collecting, creating, and saving kustomization data is executed correctly.
        """
        mock_collect.return_value = ["a.yaml", "b.yml"]
        mock_create.return_value = CommentedMap({"key": "value"})
        generate_kustomize_file("/testdir")
        mock_save.assert_called_once_with("/testdir", mock_create.return_value)
        # Resetting the mock states for the second test case
        mock_save.reset_mock()
        mock_create.reset_mock()
        mock_collect.reset_mock()
        # Testing when there are no yaml files
        mock_collect.return_value = []
        generate_kustomize_file("/testdir")
        mock_save.assert_not_called()


if __name__ == "__main__":
    unittest.main()
